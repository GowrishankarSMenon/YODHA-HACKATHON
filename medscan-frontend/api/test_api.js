const BASE_URL = 'http://localhost:5000/api';

async function test() {
    console.log('--- Testing Radiology API ---');

    // 1. Search for patient (existing one from database.py)
    const patientUhid = 'UH123456';
    console.log(`\n1. Searching for patient: ${patientUhid}`);
    try {
        const res = await fetch(`${BASE_URL}/patient/${patientUhid}`);
        const data = await res.json();
        if (res.ok) {
            console.log('✅ Patient found:', data.name);
        } else {
            console.log('❌ Patient search failed:', data.message);
        }
    } catch (err) {
        console.error('❌ Error during patient search:', err.message);
    }

    // 2. Upload lab record
    console.log('\n2. Uploading lab record...');
    try {
        const res = await fetch(`${BASE_URL}/lab-records`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                uhid: patientUhid,
                file_url: 'http://example.com/manual_upload_1.jpg',
                reviews: 'Manual entry for radiology dashboard test'
            })
        });
        const data = await res.json();
        if (res.ok) {
            console.log('✅ Lab record uploaded:', data.record_id);
        } else {
            console.log('❌ Lab record upload failed:', data.message);
        }
    } catch (err) {
        console.error('❌ Error during lab record upload:', err.message);
    }

    // 3. Search for non-existent patient
    console.log('\n3. Searching for non-existent patient: UHID-999');
    try {
        const res = await fetch(`${BASE_URL}/patient/UHID-999`);
        const data = await res.json();
        if (!res.ok) {
            console.log('✅ Correctly handled 404:', data.message);
        } else {
            console.log('❌ Unexpected success for non-existent patient');
        }
    } catch (err) {
        console.error('❌ Error during 404 test:', err.message);
    }
}

test();
