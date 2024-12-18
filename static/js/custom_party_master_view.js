document.addEventListener('DOMContentLoaded', function () {
    const partyTypeField = document.getElementById('id_party_type');
    const creditPeriodField = document.getElementById('id_credit_period').closest('.form-row');
    const poNoField = document.getElementById('id_po_no').closest('.form-row');
    const vendorCodeField = document.getElementById('id_vendor_code').closest('.form-row');
    const quotationNumberField = document.getElementById('id_quotation_number').closest('.form-row');

    const creditPeriodInput = document.getElementById('id_credit_period');
    const poNoInput = document.getElementById('id_po_no');
    const vendorCodeInput = document.getElementById('id_vendor_code');
    const quotationNumberInput = document.getElementById('id_quotation_number');

    function toggleFields() {
        const selectedValue = partyTypeField.value;
        if (selectedValue === '1') {  // ID '1' is for 'Walking'
            // Hide fields
            creditPeriodField.style.display = 'none';
            poNoField.style.display = 'none';
            vendorCodeField.style.display = 'none';
            quotationNumberField.style.display = 'none';

            // Remove required attribute when hidden
            creditPeriodInput.removeAttribute('required');
            poNoInput.removeAttribute('required');
            vendorCodeInput.removeAttribute('required');
            quotationNumberInput.removeAttribute('required');

        } else {
            // Show fields
            creditPeriodField.style.display = '';
            poNoField.style.display = '';
            vendorCodeField.style.display = '';
            quotationNumberField.style.display = '';

            // Add required attribute when visible
            creditPeriodInput.setAttribute('required', 'required');
            poNoInput.setAttribute('required', 'required');
            vendorCodeInput.setAttribute('required', 'required');
            quotationNumberInput.setAttribute('required', 'required');
        }
    }

    // Initial check
    toggleFields();

    // Add event listener to detect changes
    partyTypeField.addEventListener('change', toggleFields);
});
