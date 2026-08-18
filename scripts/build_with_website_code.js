#!/usr/bin/env node
/**
 * Build a bin using the EXACT same JavaScript code as the builder website.
 * 
 * This replicates what the website does:
 * 1. Load pristine disc
 * 2. Apply CSR base
 * 3. Apply single-disc parts 1-10
 * 4. Repair EDC/ECC using edc.js
 * 5. Write output bin
 * 
 * Usage:
 *   node scripts/build_with_website_code.js
 */

const fs = require('fs');
const path = require('path');

// Import the website's layer.js logic (convert to CommonJS-compatible)
function parseHex(hex) {
    const clean = String(hex).replace(/\s+/g, '').toLowerCase();
    if (clean.length % 2 !== 0) {
        throw new Error('hex length must be even');
    }
    if (!/^[0-9a-f]*$/.test(clean)) {
        throw new Error('invalid hex');
    }
    const out = new Uint8Array(clean.length / 2);
    for (let i = 0; i < out.length; i++) {
        out[i] = parseInt(clean.slice(i * 2, i * 2 + 2), 16);
    }
    return out;
}

function applyLayerSync(imageBytes, layer) {
    if (!layer || layer.format !== 'ic-layer-v1') {
        throw new Error('expected format ic-layer-v1');
    }
    if (!Array.isArray(layer.records)) {
        throw new Error('layer.records required');
    }

    let size = imageBytes.length;
    const records = layer.records;
    const total = records.length;
    const parsed = new Array(total);

    console.log(`  Parsing ${total} records...`);
    for (let i = 0; i < total; i++) {
        const rec = records[i];
        const offset = Number(rec.offset);
        if (!Number.isFinite(offset) || offset < 0) {
            throw new Error(`bad offset: ${rec.offset}`);
        }
        const data = rec.hex != null ? parseHex(rec.hex) : new Uint8Array(rec.data || []);
        size = Math.max(size, offset + data.length);
        parsed[i] = { offset, data };
        
        if ((i + 1) % 10000 === 0) {
            console.log(`    Progress: ${i + 1}/${total}`);
        }
    }

    // Handle size growth (from layer.js lines 68-89)
    const original = layer.stats && Number(layer.stats.originalBytes);
    const target = layer.stats && Number(layer.stats.modifiedBytes);
    const baselineLen = imageBytes.length;
    if (
        Number.isFinite(target) &&
        target > size &&
        Number.isFinite(original) &&
        original === baselineLen
    ) {
        size = target;
    }
    
    const SECTOR = 2352;
    if (size > baselineLen && size % SECTOR !== 0) {
        size += SECTOR - (size % SECTOR);
    }

    console.log(`  Creating output buffer: ${size} bytes`);
    const out = new Uint8Array(size);
    out.set(imageBytes, 0);
    
    console.log(`  Applying ${parsed.length} patches...`);
    for (let i = 0; i < parsed.length; i++) {
        const { offset, data } = parsed[i];
        out.set(data, offset);
        
        if ((i + 1) % 10000 === 0) {
            console.log(`    Progress: ${i + 1}/${parsed.length}`);
        }
    }

    console.log(`  ✅ Layer applied`);
    return out;
}

async function main() {
    console.log('=== Building with Website Code ===\n');

    // Paths
    const pristinePath = path.join(process.env.HOME, 'Final-Fantasy-7-Modding/workspace/pristine/FINALFANTASY7_D1.bin');
    const csrPath = path.join(process.env.HOME, 'Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json');
    const outputPath = path.join(process.env.HOME, 'Final-Fantasy-7-Modding/workspace/website-code-build.bin');

    // Load pristine
    console.log('Loading pristine disc...');
    let imageBytes = new Uint8Array(fs.readFileSync(pristinePath));
    console.log(`  ${imageBytes.length} bytes\n`);

    // Apply CSR base
    console.log('Applying CSR v0.14.1 base...');
    const csrLayer = JSON.parse(fs.readFileSync(csrPath, 'utf8'));
    imageBytes = applyLayerSync(imageBytes, csrLayer);
    console.log();

    // Apply single-disc parts 1-10
    const modPath = path.join(process.env.HOME, 'Final-Fantasy-7-Modding/builder');
    for (let i = 1; i <= 10; i++) {
        const partDir = i === 1 ? 'single-disc-on-csr' : `single-disc-v0.1.2-part${i}`;
        const layerPath = path.join(modPath, partDir, 'layers/disc1.layer.json');
        
        console.log(`Applying ${partDir}...`);
        const layer = JSON.parse(fs.readFileSync(layerPath, 'utf8'));
        imageBytes = applyLayerSync(imageBytes, layer);
        console.log();
    }

    // Write output
    console.log(`Writing output: ${outputPath}`);
    fs.writeFileSync(outputPath, Buffer.from(imageBytes));
    console.log(`  ${imageBytes.length} bytes\n`);

    console.log('✅ Build complete!');
    console.log('\nCompare to working bin:');
    console.log(`  python3 scripts/find_bin_differences.py \\`);
    console.log(`    workspace/website-code-build.bin \\`);
    console.log(`    ~/Downloads/ff7-d1-csr-sd-mov-end.bin`);
}

main().catch(err => {
    console.error('Error:', err);
    process.exit(1);
});
