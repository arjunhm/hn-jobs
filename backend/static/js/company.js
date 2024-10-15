let currentPage = 1;
let totalPages = 1;

//  Table

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
                    <td>
                        <button onclick="getCompanyJobs('${company.company}')">Get Jobs</button>
                    </td>
                `;
      }

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


// Company related job postings

async function getCompanyJobs(name) {
  try {
    const response = await fetch(`/company/jobs/?company=${name}`);
    const jsonData = await response.json();

    const tbody = document.getElementById('jobPostingsTable').getElementsByTagName('tbody')[0];
    tbody.innerHTML = '';

    if (Array.isArray(jsonData.data)) {
      for (const job of jsonData.data) {
        const row = tbody.insertRow();
        row.innerHTML = `
          <td>${job.job_name}</td>
          <td><a href="${job.author_link}" target="_blank">${job.author_name}</a></td>
          <td>${job.role}</td>
          <td><a href="${job.post_link}" target="_blank">Details</a></td>
          <td>${job.status}</td>
        `;
      }
      openModal();
    } else {
      console.error("Expected an array of job postings, but got:", jsonData.data);
    }
  } catch (error) {
    console.error("Error fetching company's jobs:", error);
  }
}

function openModal() {
  document.getElementById('jobModal').style.display = 'block';
}

function closeModal() {
  document.getElementById('jobModal').style.display = 'none';
}

// Pagination

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

// Misc

window.onclick = function (event) {
  const modal = document.getElementById('jobModal');
  if (event.target === modal) {
    closeModal();
  }
};

window.onload = () => {
  fetchCompanies();
};
