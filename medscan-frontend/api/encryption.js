const crypto = require('crypto');

// Encryption configuration
const ALGORITHM = 'aes-256-cbc';
const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY || crypto.randomBytes(32).toString('hex');
const IV_LENGTH = 16;

/**
 * Encrypt a string value
 * @param {string} text - Plain text to encrypt
 * @returns {string} Encrypted text in format: iv:encryptedData
 */
function encrypt(text) {
    if (!text || typeof text !== 'string') return text;

    try {
        const iv = crypto.randomBytes(IV_LENGTH);
        const key = Buffer.from(ENCRYPTION_KEY, 'hex');
        const cipher = crypto.createCipheriv(ALGORITHM, key, iv);

        let encrypted = cipher.update(text, 'utf8', 'hex');
        encrypted += cipher.final('hex');

        // Return IV + encrypted data (IV needed for decryption)
        return iv.toString('hex') + ':' + encrypted;
    } catch (error) {
        console.error('Encryption error:', error);
        return text; // Return original on error
    }
}

/**
 * Decrypt an encrypted string
 * @param {string} encryptedText - Encrypted text in format: iv:encryptedData
 * @returns {string} Decrypted plain text
 */
function decrypt(encryptedText) {
    if (!encryptedText || typeof encryptedText !== 'string') return encryptedText;

    // Check if text is actually encrypted (contains ':' separator)
    if (!encryptedText.includes(':')) return encryptedText;

    try {
        const parts = encryptedText.split(':');
        if (parts.length !== 2) return encryptedText;

        const iv = Buffer.from(parts[0], 'hex');
        const encryptedData = parts[1];
        const key = Buffer.from(ENCRYPTION_KEY, 'hex');

        const decipher = crypto.createDecipheriv(ALGORITHM, key, iv);
        let decrypted = decipher.update(encryptedData, 'hex', 'utf8');
        decrypted += decipher.final('utf8');

        return decrypted;
    } catch (error) {
        console.error('Decryption error:', error);
        return encryptedText; // Return original on error
    }
}

/**
 * Encrypt sensitive patient fields
 * @param {Object} patient - Patient object
 * @returns {Object} Patient with encrypted fields
 */
function encryptPatient(patient) {
    if (!patient) return patient;

    return {
        ...patient,
        name: encrypt(patient.name),
        phone: encrypt(patient.phone),
        abha_id: encrypt(patient.abha_id)
    };
}

/**
 * Decrypt sensitive patient fields
 * @param {Object} patient - Patient object with encrypted fields
 * @returns {Object} Patient with decrypted fields
 */
function decryptPatient(patient) {
    if (!patient) return patient;

    return {
        ...patient,
        name: decrypt(patient.name),
        phone: decrypt(patient.phone),
        abha_id: decrypt(patient.abha_id)
    };
}

/**
 * Encrypt sensitive record fields
 * @param {Object} record - Medical record object
 * @returns {Object} Record with encrypted fields
 */
function encryptRecord(record) {
    if (!record || !record.extracted_data) return record;

    const encryptedData = { ...record.extracted_data };

    // Encrypt diagnosis
    if (encryptedData.diagnosis) {
        encryptedData.diagnosis = encrypt(encryptedData.diagnosis);
    }

    // Encrypt chief complaint
    if (encryptedData.chief_complaint) {
        encryptedData.chief_complaint = encrypt(encryptedData.chief_complaint);
    }

    // Encrypt medications (as JSON string)
    if (encryptedData.medications) {
        encryptedData.medications = encrypt(JSON.stringify(encryptedData.medications));
    }

    // Encrypt treatment plan
    if (encryptedData.treatment_plan) {
        encryptedData.treatment_plan = encrypt(encryptedData.treatment_plan);
    }

    return {
        ...record,
        extracted_data: encryptedData
    };
}

/**
 * Decrypt sensitive record fields
 * @param {Object} record - Medical record with encrypted fields
 * @returns {Object} Record with decrypted fields
 */
function decryptRecord(record) {
    if (!record || !record.extracted_data) return record;

    const decryptedData = { ...record.extracted_data };

    // Decrypt diagnosis
    if (decryptedData.diagnosis) {
        decryptedData.diagnosis = decrypt(decryptedData.diagnosis);
    }

    // Decrypt chief complaint
    if (decryptedData.chief_complaint) {
        decryptedData.chief_complaint = decrypt(decryptedData.chief_complaint);
    }

    // Decrypt medications (parse JSON)
    if (decryptedData.medications) {
        try {
            const decryptedMeds = decrypt(decryptedData.medications);
            decryptedData.medications = JSON.parse(decryptedMeds);
        } catch (error) {
            // If parsing fails, it might already be an array (not encrypted)
            // Keep original value
        }
    }

    // Decrypt treatment plan
    if (decryptedData.treatment_plan) {
        decryptedData.treatment_plan = decrypt(decryptedData.treatment_plan);
    }

    return {
        ...record,
        extracted_data: decryptedData
    };
}

module.exports = {
    encrypt,
    decrypt,
    encryptPatient,
    decryptPatient,
    encryptRecord,
    decryptRecord
};
