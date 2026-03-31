/* Expense Flow - Frontend JavaScript with Eel Integration */

// Screen navigation
const screens = {
  dashboard: { title: 'Dashboard', subtitle: 'Overview' },
  companies: { title: 'Companies', subtitle: 'Manage clients' },
  addrecord: { title: 'Add Record', subtitle: 'New entry' },
  export: { title: 'Export', subtitle: 'PDF export' }
};

let currentScreen = 'dashboard';
let selectedCompanyId = null;
let companies = [];
let records = [];
let selectedProcesses = [];

function showScreen(id, navEl) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('screen-' + id).classList.add('active');
  if (navEl) navEl.classList.add('active');
  else document.querySelectorAll('.nav-item')[getScreenIndex(id)].classList.add('active');
  
  document.getElementById('topbar-page').textContent = screens[id].title;
  document.getElementById('topbar-sub').textContent = screens[id].subtitle;
  currentScreen = id;
  
  if (id === 'dashboard') loadDashboard();
  if (id === 'companies') loadCompanies();
  if (id === 'addrecord') loadAddRecord();
  if (id === 'export') loadExport();
}

function getScreenIndex(id) {
  const order = ['dashboard', 'companies', 'addrecord', 'export'];
  return order.indexOf(id);
}

// Toast notifications
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  const icons = { success: '✓', error: '✕', warning: '!' };
  toast.innerHTML = `
    <span class="toast-icon">${icons[type]}</span>
    <span>${message}</span>
  `;
  
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

/* ═══════════════════════════════════════════════════════════════
   DASHBOARD
═══════════════════════════════════════════════════════════════ */

async function loadDashboard() {
  try {
    const stats = await eel.get_dashboard_stats()();
    document.getElementById('dash-companies').textContent = stats.companies;
    document.getElementById('dash-revenue').textContent = `AED ${stats.revenue.toLocaleString()}`;
    document.getElementById('dash-records').textContent = stats.records;
    
    // Load recent entries
    const recent = await eel.get_recent_records(5)();
    const container = document.getElementById('recent-entries-container');
    
    if (recent.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">📋</div>
          <div style="font-weight:500;color:var(--text2);margin-bottom:4px">No recent entries</div>
          <div style="font-size:12px">Add a company and record to get started</div>
        </div>
      `;
    } else {
      let html = '<table class="data-table"><thead><tr><th>Client</th><th>Company</th><th>Amount</th><th>Date</th></tr></thead><tbody>';
      recent.forEach(r => {
        html += `
          <tr>
            <td style="color:var(--text);font-weight:500">${r.client_name}</td>
            <td>${r.company_name}</td>
            <td style="font-family:'DM Mono',monospace;color:var(--amber2)">AED ${r.total_amount.toLocaleString()}</td>
            <td>${formatDate(r.date)}</td>
          </tr>
        `;
      });
      html += '</tbody></table>';
      container.innerHTML = html;
    }
  } catch (e) {
    console.error('Dashboard load error:', e);
  }
}

/* ═══════════════════════════════════════════════════════════════
   COMPANIES
═══════════════════════════════════════════════════════════════ */

async function loadCompanies() {
  try {
    companies = await eel.get_all_companies()();
    renderCompanyList();
  } catch (e) {
    console.error('Companies load error:', e);
    showToast('Failed to load companies', 'error');
  }
}

function renderCompanyList() {
  const list = document.getElementById('company-list');
  if (companies.length === 0) {
    list.innerHTML = `
      <div style="padding:20px;text-align:center;color:var(--text3);">
        <div style="margin-bottom:8px;">No companies yet</div>
        <div style="font-size:12px;">Click + New to add your first company</div>
      </div>
    `;
    return;
  }
  
  let html = '';
  companies.forEach(c => {
    html += `
      <div class="company-item ${c._id === selectedCompanyId ? 'active' : ''}" onclick="selectCompany('${c._id}')">
        <div class="company-dot"></div>
        ${c.name}
      </div>
    `;
  });
  list.innerHTML = html;
}

async function selectCompany(companyId) {
  selectedCompanyId = companyId;
  renderCompanyList();
  
  const company = companies.find(c => c._id === companyId);
  if (!company) return;
  
  document.getElementById('detail-company-name').textContent = company.name;
  
  try {
    records = await eel.get_company_records(companyId)();
    const total = records.reduce((sum, r) => sum + r.total_amount, 0);
    document.getElementById('detail-company-stats').textContent = 
      `${records.length} clients · AED ${total.toLocaleString()} total`;
    
    const tbody = document.getElementById('company-records-table');
    if (records.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:40px;color:var(--text3)">No records for this company</td></tr>';
    } else {
      tbody.innerHTML = records.map((r, index) => `
        <tr style="cursor:pointer;" onclick="showRecordDetail(${index})">
          <td style="color:var(--text);font-weight:500">${r.client_name}</td>
          <td>${r.phone || '-'}</td>
          <td><span class="badge badge-${getProcessBadgeClass(r.processes.length)}">${r.processes.length} processes</span></td>
          <td style="font-family:'DM Mono',monospace;color:var(--amber2)">AED ${r.total_amount.toLocaleString()}</td>
          <td>${formatDate(r.date)}</td>
          <td><button class="btn btn-sm btn-outline" onclick="event.stopPropagation(); showRecordDetail(${index})">View</button></td>
        </tr>
      `).join('');
    }
  } catch (e) {
    console.error('Records load error:', e);
  }
}

function showRecordDetail(recordIndex) {
  const record = records[recordIndex];
  if (!record) return;
  
  // Build process details HTML
  let processesHtml = '';
  if (record.processes && record.processes.length > 0) {
    processesHtml = record.processes.map(p => {
      let amountText = `AED ${p.amount.toLocaleString()}`;
      if (p.fine) amountText += ` <span style="color:#e74c3c">(+AED ${p.fine} fine)</span>`;
      if (p.id_fee) amountText += ` <span style="color:#e74c3c">(+AED ${p.id_fee} ID fee)</span>`;
      if (p.additional) amountText += ` <span style="color:#e74c3c">(+AED ${p.additional})</span>`;
      return `
        <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border);">
          <span style="color:var(--text)">${p.name}</span>
          <span style="font-family:'DM Mono',monospace;color:var(--amber2)">${amountText}</span>
        </div>
      `;
    }).join('');
  }
  
  const modalHtml = `
    <div class="modal-overlay active" id="record-detail-modal" onclick="hideRecordDetail(event)">
      <div class="modal" onclick="event.stopPropagation()">
        <div class="modal-header">
          <div class="modal-title">${record.client_name}</div>
          <div style="font-size:12px;color:var(--text3);">${record.phone || 'No phone'} · ${formatDate(record.date)}</div>
        </div>
        <div class="modal-body">
          <div style="margin-bottom:16px;">
            <div style="font-size:10px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--amber);margin-bottom:8px;">Processes</div>
            ${processesHtml || '<div style="color:var(--text3);padding:12px 0;">No processes found</div>'}
          </div>
          <div style="border-top:1px solid var(--border);padding-top:16px;margin-top:16px;display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:14px;font-weight:600;color:var(--text);">Total Amount</span>
            <span style="font-family:'DM Mono',monospace;font-size:20px;font-weight:600;color:var(--amber2);">AED ${record.total_amount.toLocaleString()}</span>
          </div>
        </div>
        <div class="modal-footer" style="display:flex;gap:8px;justify-content:flex-end;">
          <button class="btn btn-danger" onclick="deleteRecord('${record._id}')">Delete</button>
          <button class="btn btn-primary" onclick="editRecord('${record._id}', ${recordIndex})">Update</button>
          <button class="btn btn-ghost" onclick="hideRecordDetail()">Close</button>
        </div>
      </div>
    </div>
  `;
  
  // Remove existing modal if any
  const existingModal = document.getElementById('record-detail-modal');
  if (existingModal) existingModal.remove();
  
  // Add modal to body
  document.body.insertAdjacentHTML('beforeend', modalHtml);
}

function hideRecordDetail(event) {
  if (!event || event.target.id === 'record-detail-modal') {
    const modal = document.getElementById('record-detail-modal');
    if (modal) modal.remove();
  }
}

function getProcessBadgeClass(count) {
  if (count >= 4) return 'green';
  if (count >= 2) return 'amber';
  return 'gray';
}

function showAddCompanyModal() {
  document.getElementById('add-company-modal').classList.add('active');
  document.getElementById('new-company-name').focus();
}

function hideAddCompanyModal() {
  document.getElementById('add-company-modal').classList.remove('active');
  document.getElementById('new-company-name').value = '';
}

async function addNewCompany() {
  const name = document.getElementById('new-company-name').value.trim();
  if (!name) {
    showToast('Please enter a company name', 'warning');
    return;
  }
  
  try {
    const result = await eel.add_company(name)();
    if (result.success) {
      showToast('Company added successfully');
      hideAddCompanyModal();
      loadCompanies();
    } else {
      showToast(result.error || 'Failed to add company', 'error');
    }
  } catch (e) {
    showToast('Error adding company', 'error');
  }
}

async function deleteSelectedCompany() {
  if (!selectedCompanyId) {
    showToast('Please select a company first', 'warning');
    return;
  }
  
  const company = companies.find(c => c._id === selectedCompanyId);
  if (!confirm(`Delete "${company.name}" and all its records?`)) return;
  
  try {
    const result = await eel.delete_company(selectedCompanyId)();
    if (result.success) {
      showToast('Company deleted');
      selectedCompanyId = null;
      loadCompanies();
      document.getElementById('detail-company-name').textContent = 'Select a company';
      document.getElementById('detail-company-stats').textContent = 'No company selected';
      document.getElementById('company-records-table').innerHTML = '';
    } else {
      showToast(result.error || 'Failed to delete', 'error');
    }
  } catch (e) {
    showToast('Error deleting company', 'error');
  }
}

async function exportCompanyPDF() {
  if (!selectedCompanyId) {
    showToast('Please select a company first', 'warning');
    return;
  }
  
  try {
    const result = await eel.export_company_pdf(selectedCompanyId)();
    if (result.success) {
      showToast(`PDF exported to ${result.path}`);
    } else {
      showToast(result.error || 'Export failed', 'error');
    }
  } catch (e) {
    showToast('Export error', 'error');
  }
}

/* ═══════════════════════════════════════════════════════════════
   ADD RECORD
═══════════════════════════════════════════════════════════════ */

const processConfig = {
  'Typing': { hasFine: false, hasAdditional: false },
  'Labour Fees + Insurance': { hasFine: false, hasAdditional: false },
  'Entry Permit': { hasFine: false, hasAdditional: false },
  'Change Status': { hasFine: false, hasAdditional: false },
  'Tawjeeh Class': { hasFine: false, hasAdditional: false },
  'ILOE Insurance': { hasFine: true, hasAdditional: false },
  'Medical + ID': { hasFine: false, hasIdFee: true },
  'Stamping': { hasFine: false, hasAdditional: false },
  'Renew Establishment': { hasFine: false, hasAdditional: false },
  'Update Express': { hasFine: false, hasAdditional: false },
  'Fine': { hasFine: false, hasAdditional: false }
};

async function loadAddRecord() {
  // Load companies into dropdown
  try {
    const comps = await eel.get_all_companies()();
    companies = comps; // Update global array
    const dropdown = document.getElementById('company-dropdown');
    dropdown.innerHTML = '';
    comps.forEach(c => {
      const item = document.createElement('div');
      item.className = 'company-dropdown-item';
      item.textContent = c.name;
      item.onclick = () => selectCompanyForRecord(c.name);
      dropdown.appendChild(item);
    });
  } catch (e) {
    console.error('Error loading companies:', e);
  }
}

function toggleCompanyDropdown() {
  const dropdown = document.getElementById('company-dropdown');
  dropdown.classList.toggle('active');
}

function selectCompanyForRecord(companyName) {
  const input = document.getElementById('record-company');
  input.value = companyName;
  document.getElementById('company-dropdown').classList.remove('active');
  // Trigger client loading for this company
  loadCompanyClients(companyName);
}

// Close dropdowns when clicking outside
document.addEventListener('click', function(e) {
  const companyWrapper = document.querySelector('.company-input-wrapper');
  const companyDropdown = document.getElementById('company-dropdown');
  if (companyWrapper && !companyWrapper.contains(e.target)) {
    companyDropdown.classList.remove('active');
  }
  
  const clientDropdown = document.getElementById('client-dropdown');
  const clientInput = document.getElementById('record-client-name');
  if (clientDropdown && !clientInput.contains(e.target) && !clientDropdown.contains(e.target)) {
    clientDropdown.classList.remove('active');
  }
});

// Filter companies as user types
document.getElementById('record-company').addEventListener('input', function() {
  const searchTerm = this.value.toLowerCase();
  const items = document.querySelectorAll('.company-dropdown-item');
  items.forEach(item => {
    const name = item.textContent.toLowerCase();
    item.style.display = name.includes(searchTerm) ? 'block' : 'none';
  });
});

// Process selection change handler
document.getElementById('process-select').addEventListener('change', function() {
  const process = this.value;
  const specialFields = document.getElementById('special-fields');
  const fineRow = document.getElementById('fine-row');
  const additionalRow = document.getElementById('additional-row');
  
  fineRow.style.display = 'none';
  additionalRow.style.display = 'none';
  document.getElementById('has-fine').checked = false;
  document.getElementById('has-id-fee').checked = false;
  document.getElementById('fine-amount').style.display = 'none';
  document.getElementById('id-fee').style.display = 'none';
  document.getElementById('fine-amount').value = '';
  document.getElementById('id-fee').value = '';
  
  if (process) {
    specialFields.style.display = 'block';
    
    // // Show Fine row for processes that aren't "Fine" themselves
    // if (process !== 'Fine') {
    //   fineRow.style.display = 'flex';
    // } else {
    //   fineRow.style.display = 'none';
    // }
    
    const config = processConfig[process];
    if (config && config.hasIdFee) additionalRow.style.display = 'flex';
  } else {
    specialFields.style.display = 'none';
  }
});

function toggleFineInput() {
  const checked = document.getElementById('has-fine').checked;
  document.getElementById('fine-amount').style.display = checked ? 'block' : 'none';
}

function toggleAdditionalInput() {
  const checked = document.getElementById('has-id-fee').checked;
  document.getElementById('id-fee').style.display = checked ? 'block' : 'none';
}

function addProcessToRecord() {
  const select = document.getElementById('process-select');
  const amountInput = document.getElementById('process-amount');
  const processName = select.value;
  const amount = parseFloat(amountInput.value) || 0;
  
  if (!processName) {
    showToast('Please select a process', 'warning');
    return;
  }
  
  if (amount <= 0) {
    showToast('Please enter a valid amount', 'warning');
    amountInput.focus();
    return;
  }
  
  // Check if already added
  if (selectedProcesses.find(p => p.name === processName)) {
    showToast('This process is already added', 'warning');
    return;
  }
  
  const config = processConfig[processName];
  
  // Add main process first
  selectedProcesses.push({
    name: processName,
    amount: amount,
    extra: 0,
    extraType: ''
  });
  
  // Add Fine as separate process if checked
  if (document.getElementById('has-fine').checked) {
    const fineAmount = parseFloat(document.getElementById('fine-amount').value) || 0;
    if (fineAmount > 0) {
      selectedProcesses.push({
        name: 'Fine',
        amount: fineAmount,
        extra: 0,
        extraType: ''
      });
    }
  }
  
  // Add ID fee for specific processes
  if (config && config.hasIdFee && document.getElementById('has-id-fee').checked) {
    const idFeeAmount = parseFloat(document.getElementById('id-fee').value) || 0;
    if (idFeeAmount > 0) {
      selectedProcesses.push({
        name: 'ID Fee',
        amount: idFeeAmount,
        extra: 0,
        extraType: ''
      });
    }
  }
  
  // Reset form
  select.value = '';
  amountInput.value = '';
  document.getElementById('special-fields').style.display = 'none';
  document.getElementById('has-fine').checked = false;
  document.getElementById('has-id-fee').checked = false;
  document.getElementById('fine-amount').value = '';
  document.getElementById('id-fee').value = '';
  document.getElementById('fine-amount').style.display = 'none';
  document.getElementById('id-fee').style.display = 'none';
  
  renderProcessList();
  updateTotal();
}

function removeProcess(index) {
  selectedProcesses.splice(index, 1);
  renderProcessList();
  updateTotal();
}

function renderProcessList() {
  const container = document.getElementById('process-list-items');
  if (selectedProcesses.length === 0) {
    container.innerHTML = '<div style="padding:20px;text-align:center;color:var(--text3);font-size:12px;">No processes added yet</div>';
    return;
  }
  
  container.innerHTML = selectedProcesses.map((p, i) => {
    const amount = parseFloat(p.amount) || 0;
    const fine = parseFloat(p.fine) || 0;
    const id_fee = parseFloat(p.id_fee) || 0;
    const extra = parseFloat(p.extra) || 0;
    const total = amount + fine + id_fee + extra;
    
    let extraLabel = '';
    if (fine > 0) extraLabel += ` (+AED ${fine} fine)`;
    if (id_fee > 0) extraLabel += ` (+AED ${id_fee} ID fee)`;
    if (extra > 0 && !p.extraType) extraLabel += ` (+AED ${extra})`;
    
    return `
      <div class="process-list-item">
        <span class="process-name">${p.name}${extraLabel}</span>
        <span class="process-amount">AED ${total.toLocaleString()}</span>
        <button class="remove-btn" onclick="removeProcess(${i})">Remove</button>
      </div>
    `;
  }).join('');
}

function updateTotal() {
  let total = 0;
  selectedProcesses.forEach(p => {
    const amount = parseFloat(p.amount) || 0;
    const fine = parseFloat(p.fine) || 0;
    const id_fee = parseFloat(p.id_fee) || 0;
    const extra = parseFloat(p.extra) || 0;
    total += amount + fine + id_fee + extra;
  });
  
  document.getElementById('total-display').textContent = `AED ${total.toLocaleString()}`;
  document.getElementById('proc-count').textContent = selectedProcesses.length;
  document.getElementById('proc-subtotal').textContent = `AED ${total.toLocaleString()}`;
}

// Track current company clients for dropdown
let currentCompanyClients = [];

function toggleClientDropdown() {
  const dropdown = document.getElementById('client-dropdown');
  dropdown.classList.toggle('active');
}

function selectClientForRecord(clientName) {
  const input = document.getElementById('record-client-name');
  input.value = clientName;
  document.getElementById('client-dropdown').classList.remove('active');
  onClientSelect(clientName);
}

// Load existing clients when company is selected/changed
async function loadCompanyClients(companyName) {
  const dropdown = document.getElementById('client-dropdown');
  
  if (!companyName) {
    if (dropdown) dropdown.innerHTML = '';
    return;
  }
  
  // Find company by name (case-insensitive search)
  const company = companies.find(c => c.name.toLowerCase() === companyName.toLowerCase());
  if (!company) {
    if (dropdown) dropdown.innerHTML = '';
    return;
  }
  
  try {
    // Get records for this company
    const fetchedRecords = await eel.get_company_records(company._id)();
    currentCompanyClients = fetchedRecords || [];
    
    if (dropdown) {
      if (currentCompanyClients.length > 0) {
        dropdown.innerHTML = currentCompanyClients.map(r => 
          `<div class="company-dropdown-item" onclick="selectClientForRecord('${r.client_name}')">${r.client_name}</div>`
        ).join('');
      } else {
        dropdown.innerHTML = '<div style="padding:10px;font-size:12px;color:var(--text3)">No existing clients</div>';
      }
    }
  } catch (e) {
    console.error('Failed to load clients:', e);
  }
}

// Load client data when selected from datalist
function onClientSelect(clientName) {
  if (!clientName) return;
  
  // Find the record for this client
  const record = currentCompanyClients.find(r => r.client_name === clientName);
  
  const saveBtn = document.getElementById('save-record-btn');
  
  if (record) {
    // Set edit mode
    editingRecordId = record._id;
    
    // Populate form
    document.getElementById('record-phone').value = record.phone || '';
    
    // Load processes
    selectedProcesses = JSON.parse(JSON.stringify(record.processes || [])); // Deep clone
    renderProcessList();
    updateTotal();
    
    // Change button to update mode
    if (saveBtn) {
      saveBtn.textContent = 'Update Record';
      saveBtn.onclick = function(e) {
        e.preventDefault();
        updateExistingRecord(e);
      };
    }
    
    showToast('Existing client loaded', 'success');
  } else {
    // New client mode
    editingRecordId = null;
    
    // Reset button to save mode
    if (saveBtn) {
      saveBtn.textContent = 'Save Record';
      saveBtn.onclick = submitNewRecord;
    }
  }
}

// Removed redundant saveRecord function - using submitNewRecord and updateExistingRecord instead


function clearRecordForm() {
  document.getElementById('record-company').value = '';
  document.getElementById('record-client-name').value = '';
  document.getElementById('record-phone').value = '';
  document.getElementById('process-select').value = '';
  document.getElementById('process-amount').value = '';
  document.getElementById('special-fields').style.display = 'none';
  selectedProcesses = [];
  renderProcessList();
  updateTotal();
}

/* ═══════════════════════════════════════════════════════════════
   EXPORT
═══════════════════════════════════════════════════════════════ */

async function loadExport() {
  try {
    const comps = await eel.get_all_companies()();
    const select = document.getElementById('export-company-select');
    select.innerHTML = '<option value="">Select a company...</option>';
    comps.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c._id;
      opt.textContent = c.name;
      select.appendChild(opt);
    });
  } catch (e) {
    console.error('Error loading companies for export:', e);
  }
}

async function updateExportPreview() {
  const companyId = document.getElementById('export-company-select').value;
  const previewDiv = document.getElementById('pdf-preview');
  const badge = document.getElementById('preview-badge');
  const companyLabel = document.getElementById('preview-company');
  
  if (!companyId) {
    previewDiv.innerHTML = `
      <div style="text-align:center;color:var(--text3);">
        <div style="font-size:48px;margin-bottom:16px;">📄</div>
        <div>Select a company to generate preview</div>
      </div>
    `;
    badge.textContent = 'No selection';
    badge.className = 'badge badge-gray';
    companyLabel.textContent = 'Select a company to preview';
    return;
  }
  
  try {
    const company = companies.find(c => c._id === companyId);
    const recs = await eel.get_company_records(companyId)();
    const total = recs.reduce((sum, r) => sum + r.total_amount, 0);
    
    companyLabel.textContent = `${company.name} — ${recs.length} clients`;
    badge.textContent = 'Ready to export';
    badge.className = 'badge badge-green';
    
    let rowsHtml = '';
    if (recs.length === 0) {
      rowsHtml = '<div style="padding:20px;text-align:center;color:#999;">No records to export</div>';
    } else {
      rowsHtml = recs.map(r => `
        <div class="pdf-row">
          <span>${r.client_name}</span>
          <span class="pval">AED ${r.total_amount.toLocaleString()}</span>
        </div>
      `).join('');
    }
    
    previewDiv.innerHTML = `
      <div class="pdf-preview">
        <div class="pdf-top">
          <div>
            <div class="pdf-company-name">${company.name}</div>
            <div class="pdf-subtitle">Expense Flow — Client Records</div>
            <div class="pdf-subtitle" style="margin-top:8px">Generated: ${new Date().toLocaleDateString()}</div>
          </div>
          <div class="pdf-badge">RECEIPT</div>
        </div>
        <div class="pdf-body">
          ${rowsHtml}
        </div>
        <div class="pdf-total-row">
          <span>Grand Total</span>
          <span class="t-val">AED ${total.toLocaleString()}</span>
        </div>
      </div>
    `;
  } catch (e) {
    console.error('Preview error:', e);
  }
}

async function exportToPDF() {
  const companyId = document.getElementById('export-company-select').value;
  if (!companyId) {
    showToast('Please select a company', 'warning');
    return;
  }
  
  try {
    const result = await eel.export_company_pdf(companyId)();
    if (result.success) {
      showToast(`PDF exported to ${result.path}`);
    } else {
      showToast(result.error || 'Export failed', 'error');
    }
  } catch (e) {
    showToast('Export error', 'error');
  }
}

/* ═══════════════════════════════════════════════════════════════
   RECORD DELETE & UPDATE
═══════════════════════════════════════════════════════════════ */

let editingRecordId = null;
let editingRecordIndex = null;

async function deleteRecord(recordId) {
  if (!confirm('Are you sure you want to delete this record?')) {
    return;
  }
  
  try {
    const result = await eel.delete_record(recordId)();
    if (result.success) {
      showToast('Record deleted successfully', 'success');
      hideRecordDetail();
      // Refresh the company records
      if (selectedCompanyId) {
        selectCompany(selectedCompanyId);
      }
    } else {
      showToast(result.error || 'Delete failed', 'error');
    }
  } catch (e) {
    showToast('Delete error', 'error');
  }
}

function editRecord(recordId, recordIndex) {
  const record = records[recordIndex];
  if (!record) return;
  
  editingRecordId = recordId;
  editingRecordIndex = recordIndex;
  
  hideRecordDetail();
  
  // Switch to Add Record page
  showScreen('addrecord', document.querySelectorAll('.nav-item')[2]);
  
  // Populate the form
  const companyName = document.getElementById('detail-company-name').textContent;
  document.getElementById('record-company').value = companyName;
  document.getElementById('record-client-name').value = record.client_name;
  document.getElementById('record-phone').value = record.phone || '';
  
  // Load processes
  selectedProcesses = JSON.parse(JSON.stringify(record.processes || []));
  renderProcessList();
  updateTotal();
  
  // Change save button to update mode
  const saveBtn = document.getElementById('save-record-btn');
  if (saveBtn) {
    saveBtn.textContent = 'Update Record';
    saveBtn.onclick = function(e) {
      e.preventDefault();
      updateExistingRecord(e);
    };
  }
}

async function updateExistingRecord(e) {
  if (e) e.preventDefault();
  
  if (!editingRecordId) {
    showToast('No record selected for update', 'error');
    return;
  }
  
  const companyName = document.getElementById('record-company').value.trim();
  const clientName = document.getElementById('record-client-name').value.trim();
  const phone = document.getElementById('record-phone').value.trim();
  
  if (!companyName || !clientName) {
    showToast('Company and client name required', 'error');
    return;
  }
  
  if (selectedProcesses.length === 0) {
    showToast('Add at least one process', 'error');
    return;
  }
  
  const total = selectedProcesses.reduce((sum, p) => sum + p.amount + (p.fine || 0) + (p.id_fee || 0), 0);
  
  try {
    const result = await eel.update_record(editingRecordId, clientName, phone, selectedProcesses, total)();
    if (result.success) {
      showToast('Record updated successfully', 'success');
      clearRecordForm();
      showScreen('companies', document.querySelectorAll('.nav-item')[1]);
      if (selectedCompanyId) selectCompany(selectedCompanyId);
    } else {
      showToast(result.error || 'Update failed', 'error');
    }
  } catch (e) {
    console.error('Update error:', e);
    showToast('Update error', 'error');
  }
}

function clearRecordForm() {
  document.getElementById('record-company').value = '';
  document.getElementById('record-client-name').value = '';
  document.getElementById('record-phone').value = '';
  document.getElementById('process-select').value = '';
  document.getElementById('process-amount').value = '';
  document.getElementById('special-fields').style.display = 'none';
  document.getElementById('has-fine').checked = false;
  document.getElementById('has-id-fee').checked = false;
  document.getElementById('fine-amount').value = '';
  document.getElementById('id-fee').value = '';
  document.getElementById('fine-amount').style.display = 'none';
  document.getElementById('id-fee').style.display = 'none';
  
  // Reset datalist
  const datalist = document.getElementById('client-datalist');
  if (datalist) datalist.innerHTML = '';
  currentCompanyClients = [];
  
  // Reset edit mode
  editingRecordId = null;
  editingRecordIndex = null;
  
  // Reset button
  const saveBtn = document.getElementById('save-record-btn');
  if (saveBtn) {
    saveBtn.textContent = 'Save Record';
    saveBtn.onclick = submitNewRecord;
  }
  
  selectedProcesses = [];
  renderProcessList();
  updateTotal();
}

async function submitNewRecord() {
  const companyName = document.getElementById('record-company').value.trim();
  const clientName = document.getElementById('record-client-name').value.trim();
  const phone = document.getElementById('record-phone').value.trim();
  
  if (!companyName || !clientName) {
    showToast('Company and client name required', 'error');
    return;
  }
  
  if (selectedProcesses.length === 0) {
    showToast('Add at least one process', 'error');
    return;
  }
  
  const total = selectedProcesses.reduce((sum, p) => sum + p.amount + (p.fine || 0) + (p.id_fee || 0), 0);
  
  try {
    const result = await eel.save_record(companyName, clientName, phone, selectedProcesses, total)();
    if (result.success) {
      showToast('Record saved successfully', 'success');
      clearRecordForm();
      showScreen('dashboard', document.querySelectorAll('.nav-item')[0]);
    } else {
      showToast(result.error || 'Save failed', 'error');
    }
  } catch (e) {
    showToast('Save error', 'error');
  }
}

/* ═══════════════════════════════════════════════════════════════
   UTILITIES
═══════════════════════════════════════════════════════════════ */

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  loadDashboard();
  
  // Company field - load existing clients when company changes
  const companyInput = document.getElementById('record-company');
  if (companyInput) {
    companyInput.addEventListener('input', function() {
      loadCompanyClients(this.value.trim());
    });
  }
  
  // Initialize save button click handler
  const saveBtn = document.getElementById('save-record-btn');
  if (saveBtn) {
    saveBtn.onclick = submitNewRecord;
  }
  
  // Company search functionality
  const searchInput = document.getElementById('company-search');
  if (searchInput) {
    searchInput.addEventListener('input', filterCompanyRecords);
  }
  
  // Client selection filtering
  const clientInput = document.getElementById('record-client-name');
  if (clientInput) {
    clientInput.addEventListener('focus', () => {
      if (currentCompanyClients.length > 0) {
        document.getElementById('client-dropdown').classList.add('active');
      }
    });
    
    clientInput.addEventListener('input', function() {
      const searchTerm = this.value.toLowerCase();
      const dropdown = document.getElementById('client-dropdown');
      dropdown.classList.add('active');
      
      const items = dropdown.querySelectorAll('.company-dropdown-item');
      items.forEach(item => {
        const name = item.textContent.toLowerCase();
        item.style.display = name.includes(searchTerm) ? 'block' : 'none';
      });
    });
  }
  
  // Number inputs - only accept numeric keys
  const numberInputs = document.querySelectorAll('input[type="number"]');
  numberInputs.forEach(input => {
    input.addEventListener('keydown', function(e) {
      // Allow: backspace, delete, tab, escape, enter, decimal point, arrows
      const allowedKeys = ['Backspace', 'Delete', 'Tab', 'Escape', 'Enter', '.', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'];
      
      if (allowedKeys.includes(e.key)) return;
      
      // Allow Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
      if ((e.ctrlKey || e.metaKey) && ['a', 'c', 'v', 'x'].includes(e.key.toLowerCase())) return;
      
      // Ensure it's a number key
      if (!/[0-9]/.test(e.key)) {
        e.preventDefault();
      }
    });
    
    // Also prevent non-numeric paste
    input.addEventListener('paste', function(e) {
      const pasteData = e.clipboardData.getData('text');
      if (!/^\d*\.?\d*$/.test(pasteData)) {
        e.preventDefault();
      }
    });
  });
  
  // Disable right-click context menu
  document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
    return false;
  });
  
  // Disable F12 (DevTools), Ctrl+Shift+F (search), Ctrl+Shift+I (DevTools)
  document.addEventListener('keydown', function(e) {
    // F12
    if (e.key === 'F12') {
      e.preventDefault();
      return false;
    }
    
    // Ctrl+Shift+F or Ctrl+Shift+I
    if (e.ctrlKey && e.shiftKey && (e.key === 'f' || e.key === 'F' || e.key === 'i' || e.key === 'I')) {
      e.preventDefault();
      return false;
    }
    
    // Ctrl+Shift+J (console)
    if (e.ctrlKey && e.shiftKey && (e.key === 'j' || e.key === 'J')) {
      e.preventDefault();
      return false;
    }
    
    // Ctrl+U (view source)
    if (e.ctrlKey && (e.key === 'u' || e.key === 'U')) {
      e.preventDefault();
      return false;
    }
  });
});

// Filter records based on search input
function filterCompanyRecords() {
  const searchTerm = document.getElementById('company-search').value.toLowerCase().trim();
  const tbody = document.getElementById('company-records-table');
  
  if (!records || records.length === 0) return;
  
  const filteredRecords = records.filter((r, index) => {
    const nameMatch = r.client_name.toLowerCase().includes(searchTerm);
    const phoneMatch = (r.phone || '').toLowerCase().includes(searchTerm);
    return nameMatch || phoneMatch;
  });
  
  if (filteredRecords.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:40px;color:var(--text3)">No matching records found</td></tr>';
  } else {
    tbody.innerHTML = filteredRecords.map((r, index) => {
      const originalIndex = records.indexOf(r);
      return `
        <tr style="cursor:pointer;" onclick="showRecordDetail(${originalIndex})">
          <td style="color:var(--text);font-weight:500">${r.client_name}</td>
          <td>${r.phone || '-'}</td>
          <td><span class="badge badge-${getProcessBadgeClass(r.processes.length)}">${r.processes.length} processes</span></td>
          <td style="font-family:'DM Mono',monospace;color:var(--amber2)">AED ${r.total_amount.toLocaleString()}</td>
          <td>${formatDate(r.date)}</td>
          <td><button class="btn btn-sm btn-outline" onclick="event.stopPropagation(); showRecordDetail(${originalIndex})">View</button></td>
        </tr>
      `;
    }).join('');
  }
}
