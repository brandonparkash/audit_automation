function openAddModal() { document.getElementById('addModal').style.display = 'flex'; }
function closeAddModal() { document.getElementById('addModal').style.display = 'none'; }

function openEmailModal(email, docType, secKey) {
    const modal = document.getElementById('emailModal');
    const editor = document.getElementById('emailEditor');
    
    // THIS GENERATES THE SECURE LINK
    const secureLink = `${window.location.origin}/upload/${secKey}`;

    editor.value = `To: ${email}
Subject: ACTION REQUIRED: ISO 9001 Audit Evidence - ${docType}

Dear Colleague,

As part of our upcoming Internal Audit, we require the following documentation for the Evidence Vault:

Document: ${docType}

Please upload the file securely using this unique link:
${secureLink}

Deadline: [Date]

Kind regards,

Building Services Project Manager`;
    
    modal.style.display = 'flex';
}

function closeEmailModal() { document.getElementById('emailModal').style.display = 'none'; }

function copyEmail() {
    const editor = document.getElementById('emailEditor');
    editor.select();
    document.execCommand('copy');
    alert("Email copied to clipboard!");
}
