/**
 * Generates a random date within the last 2 years
 * @returns {string} Date in YYYY-MM-DD format
 */
function generateRandomDate() {
  const now = new Date();
  const twoYearsAgo = new Date(now.getFullYear() - 2, now.getMonth(), now.getDate());
  const randomTime = twoYearsAgo.getTime() + Math.random() * (now.getTime() - twoYearsAgo.getTime());
  const randomDate = new Date(randomTime);
  
  const year = randomDate.getFullYear();
  const month = String(randomDate.getMonth() + 1).padStart(2, '0');
  const day = String(randomDate.getDate()).padStart(2, '0');
  
  return `${year}-${month}-${day}`;
}

/**
 * Transforms raw API data into UI-ready data
 * @param {Object} record - Raw API record
 * @param {string} record.record_id - Unique record identifier
 * @param {string} record.document_type - Type of document
 * @param {Object} record.extracted_data - Extracted data from the document
 * @param {number} record.confidence_score - Confidence score of extraction
 * @returns {Object} Transformed record with UI-ready fields
 */
export function adaptRecord(record) {
  // Create a copy of the record to avoid mutating the original
  const adaptedRecord = { ...record };
  
  // Ensure extracted_data exists
  if (!adaptedRecord.extracted_data) {
    adaptedRecord.extracted_data = {};
  }
  
  // Add file_url if missing
  if (!adaptedRecord.file_url) {
    adaptedRecord.file_url = 'https://rxresu.me/assets/samples/sample-medical-report.jpg';
  }
  
  // Add visit_date if missing
  if (!adaptedRecord.visit_date) {
    adaptedRecord.visit_date = generateRandomDate();
  }
  
  // Add doctor_name if missing
  if (!adaptedRecord.doctor_name) {
    adaptedRecord.doctor_name = 'Dr. Unassigned';
  }
  
  return adaptedRecord;
}
