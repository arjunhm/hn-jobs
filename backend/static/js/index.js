let currentPage = 1;
let totalPages = 1;
statusOptions = [];

function saveState() {
  const state = {
    tableFilter: document.getElementById('tableFilter').value,
    statusFilter: document.getElementById('statusFilter').value,
    searchField: document.getElementById('searchField').value,
    tagsField: document.getElementById('tagsField').value,
    currentPage: currentPage
  };
  localStorage.setItem('jobSearchState', JSON.stringify(state));
}

function loadState() {
  const savedState = JSON.parse(localStorage.getItem('jobSearchState'));
  if (savedState) {
    document.getElementById('tableFilter').value = savedState.tableFilter || '';
    document.getElementById('statusFilter').value = savedState.statusFilter || '';
    document.getElementById('searchField').value = savedState.searchField || '';
    document.getElementById('tagsField').value = savedState.tagsField || '';
    currentPage = savedState.currentPage || 1;
  }
}

// get list of job-posting tables
async function fetchTables() {
  try {
    const response = await fetch('/tables');
    const json_response = await response.json();
    const dbSelect = document.getElementById('tableFilter');
    dbSelect.innerHTML = '';

    // populate table filter dropdown
    for (let i = 0; i < json_response.data.length; i++) {
      const option = document.createElement('option');
      option.value = json_response.data[i];
      option.text = json_response.data[i];
      dbSelect.appendChild(option);
    }
    loadState();
  } catch (error) {
    console.error('Error fetching tables:', error);
  }
}

// fetch status list
async function fetchStatusOptions() {
  try {
    const response = await fetch('/status');
    const data = await response.json();
    const statusSelect = document.getElementById('statusFilter');
    statusSelect.innerHTML = '';
    statusOptions = data.status;

    // populate status filter dropdown
    for (const status of data.status) {
      const option = document.createElement('option');
      option.value = status;
      option.text = status.charAt(0).toUpperCase() + status.slice(1);
      statusSelect.appendChild(option);
    }
    loadState();
  } catch (error) {
    console.error('Error fetching status options:', error);
  }
}

// search jobs
async function searchJobs(page = 1) {
  const search = document.getElementById('searchField').value.trim();
  const tags = document.getElementById('tagsField').value.trim();
  const status = document.getElementById('statusFilter').value;
  const table = document.getElementById('tableFilter').value;

  // Fetch jobs with the current search term and page number
  const response = await fetch(`/jobs/${status}/${table}?page=${page}&per_page=10&search=${search}&tags=${tags}`);
  const json_response = await response.json();

  if (Array.isArray(json_response.data)) {
    const tbody = document.getElementById('jobTable').getElementsByTagName('tbody')[0];
    tbody.innerHTML = '';

    for (const job of json_response.data) {
      const row = tbody.insertRow();
      const linksHTML = job.links
        .split(' ')
        .map(link => `<a href="${link}" target="_blank">${link}</a>`)
        .join('<br>');
      row.innerHTML = `
                <td>${job.job_name}</td>
                <td>
                    <a href="${job.author_link}" target="_blank">${job.author_name}</a>
                    |
                    <a href="${job.post_link}" target="_blank">Link</a>
                </td>
                <td>${job.role}</td>
                <td>${job.body}</td>
                <td>${linksHTML}</td>
                <td>
                    <select id="status_${job.job_name}"></select>
                </td>
                <td>
                    <button class="button" onclick="updateJobStatus('${job.job_name}')">Update</button>
                </td>
            `;
      populateStatusDropdowns(job);
      saveState();
    }

    // Update pagination info
    currentPage = page; // Update current page
    totalPages = data.total_pages;
    document.getElementById('totalPages').textContent = `${totalPages}`;
    document.getElementById('currentPage').value = `${currentPage}`;
    document.getElementById('prevPage').disabled = currentPage <= 1; // Disable previous button if on first page
    document.getElementById('nextPage').disabled = currentPage >= totalPages; // Disable next button if on last page
  } else {
    console.error('Expected jobs to be an array, but got:', data.jobs);
  }
}

function populateStatusDropdowns(job) {
  const statusDropdown = document.getElementById(`status_${job.job_name}`);
  statusDropdown.innerHTML = '';

  for (let i = 0; i < statusOptions.length; i++) {
    if (statusOptions[i] == "all") {
      continue;
    }
    const option = document.createElement('option');
    option.value = statusOptions[i];
    option.textContent = statusOptions[i].charAt(0).toUpperCase() + statusOptions[i].slice(1);
    if (statusOptions[i] === job.status) {
      option.selected = true;
    }
    statusDropdown.appendChild(option);
  }
}

function changePage(direction) {
  const newPage = currentPage + direction;

  if (newPage > 0 && newPage <= totalPages) {
    searchJobs(newPage);
  }
}

function GoToPage() {
  const page = parseInt(document.getElementById('currentPage').value, 10);
  if (page > 0 && page <= totalPages) {
    searchJobs(page);
  }
}

async function updateData() {

  const response = await fetch(`/update/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
  });

  if (response.ok) {
    alert("Update successful");
  } else {
    alert('Failed to update data');
  }
}

async function updateJobStatus(jobName) {
  const status = document.getElementById(`status_${jobName}`).value;
  const table = document.getElementById('tableFilter').value;

  const response = await fetch(`/jobs/update/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      job_name: jobName,
      table_name: table,
      status: status
    })
  });

  if (response.ok) {
    // alert(`Job status updated to ${status}`);
  } else {
    alert('Failed to update job status');
  }
}

// Fetch initial data
window.onload = async () => {
  await fetchTables();
  await fetchStatusOptions();
  loadState();
  searchJobs();
};