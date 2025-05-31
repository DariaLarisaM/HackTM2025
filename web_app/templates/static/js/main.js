(function () {
    "use strict";

    /**
     * Apply .scrolled class to the body as the page is scrolled down
     */
    function toggleScrolled() {
        const selectBody = document.querySelector('body');
        const selectHeader = document.querySelector('#header');
        if (!selectHeader.classList.contains('scroll-up-sticky') && !selectHeader.classList.contains('sticky-top') && !selectHeader.classList.contains('fixed-top')) return;
        window.scrollY > 100 ? selectBody.classList.add('scrolled') : selectBody.classList.remove('scrolled');
    }

    document.addEventListener('scroll', toggleScrolled);
    window.addEventListener('load', toggleScrolled);

    const mobileNavToggleBtn = document.querySelector('.mobile-nav-toggle');

    function mobileNavToogle() {
        document.querySelector('body').classList.toggle('mobile-nav-active');
        mobileNavToggleBtn.classList.toggle('bi-list');
        mobileNavToggleBtn.classList.toggle('bi-x');
    }
    if (mobileNavToggleBtn) {
        mobileNavToggleBtn.addEventListener('click', mobileNavToogle);
    }

    const preloader = document.querySelector('#preloader');
    if (preloader) {
        window.addEventListener('load', () => {
            preloader.remove();
        });
    }

    let scrollTop = document.querySelector('.scroll-top');

    function toggleScrollTop() {
        if (scrollTop) {
            window.scrollY > 100 ? scrollTop.classList.add('active') : scrollTop.classList.remove('active');
        }
    }
    scrollTop.addEventListener('click', (e) => {
        e.preventDefault();
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    window.addEventListener('load', toggleScrollTop);
    document.addEventListener('scroll', toggleScrollTop);

    /**
     * Animation on scroll function and init
     */
    function aosInit() {
        AOS.init({
            duration: 600,
            easing: 'ease-in-out',
            once: true,
            mirror: false
        });
    }

    window.addEventListener('load', aosInit);

    window.addEventListener('load', function (e) {
        if (window.location.hash) {
            if (document.querySelector(window.location.hash)) {
                setTimeout(() => {
                    let section = document.querySelector(window.location.hash);
                    let scrollMarginTop = getComputedStyle(section).scrollMarginTop;
                    window.scrollTo({
                        top: section.offsetTop - parseInt(scrollMarginTop),
                        behavior: 'smooth'
                    });
                }, 100);
            }
        }
    });

    let navmenulinks = document.querySelectorAll('.navmenu a');

    function navmenuScrollspy() {
        navmenulinks.forEach(navmenulink => {
            if (!navmenulink.hash) return;
            let section = document.querySelector(navmenulink.hash);
            if (!section) return;
            let position = window.scrollY + 200;
            if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
                document.querySelectorAll('.navmenu a.active').forEach(link => link.classList.remove('active'));
                navmenulink.classList.add('active');
            } else {
                navmenulink.classList.remove('active');
            }
        })
    }
    window.addEventListener('load', navmenuScrollspy);
    document.addEventListener('scroll', navmenuScrollspy);

})();

document.getElementById('upload-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const message = document.getElementById('upload-message');

    if (fileInput.files.length === 0) {
        document.getElementById('alert-box').style.display = 'block';
        return;
    }

    message.style.color = 'green';
    message.innerText = 'The document "' + fileInput.files[0].name + '" was successfully uploaded!';
    message.style.display = 'block';

    fileInput.value = '';
});

const documentsContainer = document.getElementById('documentsContainer');
const noDocsMsg = document.getElementById('noDocsMsg');
const goToUploadBtn = document.getElementById('goToUploadBtn');
const uploadForm = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');

let uploadedDocs = [];

function renderDocuments() {
    documentsContainer.innerHTML = '';

    if (uploadedDocs.length === 0) {
        noDocsMsg.style.display = 'block';
        documentsContainer.style.display = 'none';
    } else {
        noDocsMsg.style.display = 'none';
        documentsContainer.style.display = 'grid';

        uploadedDocs.forEach((doc, index) => {
            const docDiv = document.createElement('div');
            docDiv.style = `
        background-color: #f0f4ff; 
        padding: 15px 20px; 
        border-radius: 12px; 
        width: 100%; 
        max-width: 220px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        position: relative;
        font-weight: 600;
        font-size: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
      `;

            const nameSpan = document.createElement('span');
            nameSpan.textContent = doc;

            const removeBtn = document.createElement('button');
            removeBtn.textContent = '×';
            removeBtn.style = `
        background: none;
        border: none;
        color: #900;
        font-size: 1.5rem;
        cursor: pointer;
        line-height: 1;
        padding: 0 8px 2px 8px;
        font-weight: 700;
      `;
            removeBtn.title = 'Delete document';
            removeBtn.onclick = () => {
                uploadedDocs.splice(index, 1);
                renderDocuments();
            };

            docDiv.appendChild(nameSpan);
            docDiv.appendChild(removeBtn);

            documentsContainer.appendChild(docDiv);
        });
    }
}

goToUploadBtn.addEventListener('click', () => {
    const uploadSection = document.getElementById('documents');
    if (uploadSection) {
        uploadSection.scrollIntoView({ behavior: 'smooth' });
    }
});

document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        alert('Please select a document!');
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch('https://localhost:5001/api/documents/upload', {
        method: 'POST',
        body: formData
    });

    if (res.ok) {
        alert('Document uploaded!');
        fileInput.value = '';
        loadDocuments(); // reload the list
    }
});

async function loadDocuments() {
    const response = await fetch('https://localhost:5001/api/documents/list');
    const docs = await response.json();

    const container = document.getElementById('document-list');
    container.innerHTML = '';

    if (docs.length === 0) {
        document.getElementById('no-documents-message').style.display = 'block';
    } else {
        document.getElementById('no-documents-message').style.display = 'none';
        docs.forEach(doc => {
            const box = document.createElement('div');
            box.className = 'document-box';
            box.innerHTML = `
        <span class="document-name">${doc.name}</span>
        <button onclick="deleteDocument(${doc.id})" class="remove-document">&times;</button>
      `;
            container.appendChild(box);
        });
    }
}

async function deleteDocument(id) {
    if (!confirm('Are you sure you want to delete this document?')) return;

    const res = await fetch(`https://localhost:5001/api/documents/delete/${id}`, {
        method: 'DELETE'
    });

    if (res.ok) {
        loadDocuments(); // reload the list
    }
}