let currentPage = 1;
let totalPages = 1;

async function fetchCompanies(page = 1) {
    try {
        const response = await fetch(`/companies/?page=${page}&per_page=30`);
        const jsonData = await response.json();
        
        if (Array.isArray(jsonData.data)) {
            const tbody = document.getElementById('companyTable').getElementsByTagName('tbody')[0];
            tbody.innerHTML = '';

            for (const company of jsonData.data) {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${company.company}</td>
                    <td><a href="${company.link}" target="_blank">${company.link}</a></td>
                    <td>${company.visa}</td>
                `;
            }

            // Update pagination info
            currentPage = page;
            totalPages = jsonData.total_pages;
            document.getElementById('totalPages').textContent = `${totalPages}`;
            document.getElementById('currentPage').value = `${currentPage}`;
            document.getElementById('prevPage').disabled = currentPage <= 1;
            document.getElementById('nextPage').disabled = currentPage >= totalPages;
        } else {
            console.error('Expected an array of companies, but got:', jsonData.data);
        }
    } catch (error) {
        console.error('Error fetching companies:', error);
    }
}

function changePage(direction) {
    const newPage = currentPage + direction;
    if (newPage > 0 && newPage <= totalPages) {
        fetchCompanies(newPage);
    }
}

function goToPage() {
    const page = parseInt(document.getElementById('currentPage').value, 10);
    if (page > 0 && page <= totalPages) {
        fetchCompanies(page);
    }
}

// Fetch the initial list of companies on page load
window.onload = () => {
    fetchCompanies();
};
