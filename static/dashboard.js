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

    // Only attach click event to the drop container
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
            fileInput.files = files;
            console.log(`${files.length} file(s) dropped.`);
        }
    }

    // Export functionality for modal export buttons
    const exportJsonBtnModal = document.getElementById('modal-export-json-btn');
    const exportCsvBtnModal = document.getElementById('modal-export-csv-btn');
    const exportPdfBtnModal = document.getElementById('modal-export-pdf-btn');

    // Helper function to trigger file download
    function downloadFile(url, filename) {
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    // Export Modal Content as JSON
    exportJsonBtnModal.addEventListener('click', function () {
        const cardElem = document.querySelector('.card[data-details]');
        if (!cardElem) return;
        const modalData = JSON.parse(cardElem.getAttribute('data-details'));
        const dataStr = JSON.stringify(modalData, null, 2);
        const blob = new Blob([dataStr], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        downloadFile(url, "modal_exported_document.json");
    });

    // Export Modal Content as CSV
    exportCsvBtnModal.addEventListener('click', function () {
        const cardElem = document.querySelector('.card[data-details]');
        if (!cardElem) return;
        const modalData = JSON.parse(cardElem.getAttribute('data-details'));
        let csvContent = "data:text/csv;charset=utf-8,";
        // Header row
        const header = ["Licensor", "Licensee", "Effective Date", "Term Duration", "Scope of Use", "License Fee", "Royalty Terms"];
        csvContent += header.join(",") + "\n";
        // Construct row with fallback to "N/A"
        const scopeOfUse = (modalData.licensing_terms?.scope_of_use && Array.isArray(modalData.licensing_terms.scope_of_use))
            ? modalData.licensing_terms.scope_of_use.join(" | ")
            : "N/A";
        const row = [
            modalData.parties?.licensor || "N/A",
            modalData.parties?.licensee || "N/A",
            modalData.licensing_terms?.effective_date || "N/A",
            modalData.licensing_terms?.term_duration || "N/A",
            scopeOfUse,
            modalData.financial_terms?.license_fee || "N/A",
            modalData.financial_terms?.royalty_terms || "N/A"
        ];
        csvContent += row.join(",") + "\n";
        const encodedUri = encodeURI(csvContent);
        downloadFile(encodedUri, "modal_exported_document.csv");
    });

    exportPdfBtnModal.addEventListener('click', function () {
        const myJsPDF = window.jspdf.jsPDF;
        if (!myJsPDF) {
            alert("PDF export requires jsPDF library. Please include it.");
            return;
        }
    
        const cardElem = document.querySelector('.card[data-details]');
        if (!cardElem) return;
        const modalData = JSON.parse(cardElem.getAttribute('data-details'));
        const doc = new myJsPDF();
    
        let y = 10;
        const lineHeight = 8;
        const margin = 10;
        const pageHeight = doc.internal.pageSize.height;
    
        // Helper to wrap text and handle page breaks
        function addWrappedText(label, value) {
            const text = `${label}: ${value}`;
            const splitText = doc.splitTextToSize(text, 180); // 180 = width of text box
            for (let i = 0; i < splitText.length; i++) {
                if (y + lineHeight > pageHeight - margin) {
                    doc.addPage();
                    y = margin;
                }
                doc.text(splitText[i], margin, y);
                y += lineHeight;
            }
        }
    
        // Add content
        addWrappedText("Licensor", modalData.parties?.licensor || "N/A");
        addWrappedText("Licensee", modalData.parties?.licensee || "N/A");
        addWrappedText("Effective Date", modalData.licensing_terms?.effective_date || "N/A");
        addWrappedText("Term Duration", modalData.licensing_terms?.term_duration || "N/A");
        addWrappedText("Scope of Use", modalData.licensing_terms?.scope_of_use?.join(", ") || "N/A");
        addWrappedText("Exclusivity", modalData.licensing_terms?.license_characteristics?.exclusivity || "N/A");
        addWrappedText("Transferability", modalData.licensing_terms?.license_characteristics?.transferability || "N/A");
        addWrappedText("Geographical Scope", modalData.licensing_terms?.license_characteristics?.geographical_scope || "N/A");
        addWrappedText("User Access", modalData.licensing_terms?.license_characteristics?.user_access || "N/A");
        addWrappedText("License Fee", modalData.financial_terms?.license_fee || "N/A");
        addWrappedText("Royalty Terms", modalData.financial_terms?.royalty_terms || "N/A");
        addWrappedText("Indemnification", modalData.legal_compliance?.indemnification || "N/A");
        addWrappedText("Liability Limitations", modalData.legal_compliance?.liability_limitations || "N/A");
        addWrappedText("Termination Grounds", modalData.contract_termination?.termination_grounds?.join(" | ") || "N/A");
        addWrappedText("Governing Law", modalData.contract_termination?.dispute_resolution?.governing_law || "N/A");
        addWrappedText("Resolution Mechanism", modalData.contract_termination?.dispute_resolution?.resolution_mechanism || "N/A");
        addWrappedText("Attribution Requirements", modalData.intellectual_property?.attribution_requirements || "N/A");
    
        doc.save("exported_document.pdf");
    });
    
    

    // Attach event listener for view-details buttons
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
        html += `<p><strong>Licensor:</strong> ${data.parties?.licensor || "N/A"}</p>`;
        html += `<p><strong>Licensee:</strong> ${data.parties?.licensee || "N/A"}</p>`;
        html += `<h3>Licensing Terms</h3>`;
        html += `<p><strong>Effective Date:</strong> ${data.licensing_terms?.effective_date || "N/A"}</p>`;
        html += `<p><strong>Term Duration:</strong> ${data.licensing_terms?.term_duration || "N/A"}</p>`;
        html += `<p><strong>Scope of Use:</strong> ${(data.licensing_terms?.scope_of_use && Array.isArray(data.licensing_terms.scope_of_use)) ? data.licensing_terms.scope_of_use.join(', ') : "N/A"}</p>`;
        html += `<p><strong>License Characteristics:</strong></p>`;
        html += `<ul>`;
        html += `<li><strong>Exclusivity:</strong> ${data.licensing_terms?.license_characteristics?.exclusivity || "N/A"}</li>`;
        html += `<li><strong>Transferability:</strong> ${data.licensing_terms?.license_characteristics?.transferability || "N/A"}</li>`;
        html += `<li><strong>Geographical Scope:</strong> ${data.licensing_terms?.license_characteristics?.geographical_scope || "N/A"}</li>`;
        html += `<li><strong>User Access:</strong> ${data.licensing_terms?.license_characteristics?.user_access || "N/A"}</li>`;
        html += `</ul>`;
        html += `<h3>Financial Terms</h3>`;
        html += `<p><strong>License Fee:</strong> ${data.financial_terms?.license_fee || "N/A"}</p>`;
        html += `<p><strong>Royalty Terms:</strong> ${data.financial_terms?.royalty_terms || "N/A"}</p>`;
        html += `<h3>Usage Restrictions</h3>`;
        html += `<ul>`;
        if (data.usage_restrictions?.prohibited_uses && Array.isArray(data.usage_restrictions.prohibited_uses)) {
            data.usage_restrictions.prohibited_uses.forEach(function(item) {
                html += `<li>${item}</li>`;
            });
        } else {
            html += `<li>N/A</li>`;
        }
        html += `</ul>`;
        html += `<h3>Intellectual Property</h3>`;
        html += `<p><strong>Copyright Ownership:</strong> ${data.intellectual_property?.copyright_ownership || "N/A"}</p>`;
        html += `<p><strong>Attribution Requirements:</strong> ${data.intellectual_property?.attribution_requirements || "N/A"}</p>`;
        html += `<h3>Legal Compliance</h3>`;
        html += `<p><strong>Third Party Rights:</strong> ${data.legal_compliance?.third_party_rights || "N/A"}</p>`;
        html += `<p><strong>Indemnification:</strong> ${data.legal_compliance?.indemnification || "N/A"}</p>`;
        html += `<p><strong>Liability Limitations:</strong> ${data.legal_compliance?.liability_limitations || "N/A"}</p>`;
        html += `<h3>Contract Termination</h3>`;
        html += `<p><strong>Termination Grounds:</strong></p>`;
        html += `<ul>`;
        if (data.contract_termination?.termination_grounds && Array.isArray(data.contract_termination.termination_grounds)) {
            data.contract_termination.termination_grounds.forEach(function(item) {
                html += `<li>${item}</li>`;
            });
        } else {
            html += `<li>N/A</li>`;
        }
        html += `</ul>`;
        html += `<p><strong>Dispute Resolution:</strong></p>`;
        html += `<ul>`;
        html += `<li><strong>Governing Law:</strong> ${data.contract_termination?.dispute_resolution?.governing_law || "N/A"}</li>`;
        html += `<li><strong>Resolution Mechanism:</strong> ${data.contract_termination?.dispute_resolution?.resolution_mechanism || "N/A"}</li>`;
        html += `</ul>`;
        return html;
    }
});
