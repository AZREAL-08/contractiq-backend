document.addEventListener('DOMContentLoaded', function () {
    console.log("Dashboard JS loaded.");

    const dropArea = document.getElementById('drop-area');
    const dropContainer = document.querySelector('.drop-container');
    const fileInput = document.getElementById('file');
    const uploadBtn = document.querySelector('.upload-btn');

    // Prevent default drag behaviors on drop area and document
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight drop area when file is dragged over drop container
    ['dragenter', 'dragover'].forEach(eventName => {
        dropContainer.addEventListener(eventName, () => dropArea.classList.add('highlight'), false);
    });
    ['dragleave', 'drop'].forEach(eventName => {
        dropContainer.addEventListener(eventName, () => dropArea.classList.remove('highlight'), false);
    });

    // Only attach click event to the drop container, not the whole drop area
    dropContainer.addEventListener('click', function () {
        fileInput.click();
    });

    // Prevent upload button click from propagating to drop area
    uploadBtn.addEventListener('click', function(e) {
        e.stopPropagation();
    });

    // Handle drop event: set dropped files into file input
    dropArea.addEventListener('drop', handleDrop, false);
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files && files.length) {
            // Assign the dropped files to the file input element
            fileInput.files = files;
            console.log(`${files.length} file(s) dropped.`);
        }
    }

    // Attach event listener for view-details buttons (if any)
    const viewButtons = document.querySelectorAll('.view-details-btn');
    console.log(`Found ${viewButtons.length} view-details buttons.`);
    viewButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            console.log("View details button clicked.");
            const card = this.closest('.card');
            try {
                const detailsData = JSON.parse(card.getAttribute('data-details'));
                const modalBody = document.getElementById("modalBody");
                modalBody.innerHTML = renderModalContent(detailsData);
                document.getElementById("detailsModal").style.display = "block";
            } catch (error) {
                console.error("Error parsing card data:", error);
            }
        });
    });

    // Modal close functionality
    const modal = document.getElementById("detailsModal");
    const closeBtn = document.querySelector(".close-btn");
    closeBtn.addEventListener('click', () => modal.style.display = "none");
    window.addEventListener('click', function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

    // Helper function to render modal content from data
    function renderModalContent(data) {
        let html = `<h2>Document Details</h2>`;
        html += `<h3>Parties</h3>`;
        html += `<p><strong>Licensor:</strong> ${data.parties.licensor}</p>`;
        html += `<p><strong>Licensee:</strong> ${data.parties.licensee}</p>`;
        html += `<h3>Licensing Terms</h3>`;
        html += `<p><strong>Effective Date:</strong> ${data.licensing_terms.effective_date}</p>`;
        html += `<p><strong>Term Duration:</strong> ${data.licensing_terms.term_duration}</p>`;
        html += `<p><strong>Scope of Use:</strong> ${data.licensing_terms.scope_of_use.join(', ')}</p>`;
        html += `<p><strong>License Characteristics:</strong></p>`;
        html += `<ul>`;
        html += `<li><strong>Exclusivity:</strong> ${data.licensing_terms.license_characteristics.exclusivity}</li>`;
        html += `<li><strong>Transferability:</strong> ${data.licensing_terms.license_characteristics.transferability}</li>`;
        html += `<li><strong>Geographical Scope:</strong> ${data.licensing_terms.license_characteristics.geographical_scope}</li>`;
        html += `<li><strong>User Access:</strong> ${data.licensing_terms.license_characteristics.user_access}</li>`;
        html += `</ul>`;
        html += `<h3>Financial Terms</h3>`;
        html += `<p><strong>License Fee:</strong> ${data.financial_terms.license_fee}</p>`;
        html += `<p><strong>Royalty Terms:</strong> ${data.financial_terms.royalty_terms}</p>`;
        html += `<h3>Usage Restrictions</h3>`;
        html += `<ul>`;
        data.usage_restrictions.prohibited_uses.forEach(function(item) {
            html += `<li>${item}</li>`;
        });
        html += `</ul>`;
        html += `<h3>Intellectual Property</h3>`;
        html += `<p><strong>Copyright Ownership:</strong> ${data.intellectual_property.copyright_ownership}</p>`;
        html += `<p><strong>Attribution Requirements:</strong> ${data.intellectual_property.attribution_requirements}</p>`;
        html += `<h3>Legal Compliance</h3>`;
        html += `<p><strong>Third Party Rights:</strong> ${data.legal_compliance.third_party_rights}</p>`;
        html += `<p><strong>Indemnification:</strong> ${data.legal_compliance.indemnification}</p>`;
        html += `<p><strong>Liability Limitations:</strong> ${data.legal_compliance.liability_limitations}</p>`;
        html += `<h3>Contract Termination</h3>`;
        html += `<p><strong>Termination Grounds:</strong></p>`;
        html += `<ul>`;
        data.contract_termination.termination_grounds.forEach(function(item) {
            html += `<li>${item}</li>`;
        });
        html += `</ul>`;
        html += `<p><strong>Dispute Resolution:</strong></p>`;
        html += `<ul>`;
        html += `<li><strong>Governing Law:</strong> ${data.contract_termination.dispute_resolution.governing_law}</li>`;
        html += `<li><strong>Resolution Mechanism:</strong> ${data.contract_termination.dispute_resolution.resolution_mechanism}</li>`;
        html += `</ul>`;
        return html;
    }
});
