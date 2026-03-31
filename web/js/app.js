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
        <div class="modal-footer">
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
  'Update Express': { hasFine: false, hasAdditional: false }
};

async function loadAddRecord() {
  // Load companies into dropdown
  try {
    const comps = await eel.get_all_companies()();
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
  document.getElementById('record-company').value = companyName;
  document.getElementById('company-dropdown').classList.remove('active');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(e) {
  const wrapper = document.querySelector('.company-input-wrapper');
  const dropdown = document.getElementById('company-dropdown');
  if (wrapper && !wrapper.contains(e.target)) {
    dropdown.classList.remove('active');
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
    const config = processConfig[process];
    if (config.hasFine) fineRow.style.display = 'flex';
    if (config.hasAdditional) additionalRow.style.display = 'flex';
  } else {
    specialFields.style.display = 'none';
  }
});

function toggleFineInput() {
  const checked = document.getElementById('has-fine').checked;
  document.getElementById('fine-amount').style.display = checked ? 'block' : 'none';
}

function toggleAdditionalInput() {
  const checked = document.getElementById('has-additional').checked;
  document.getElementById('additional-amount').style.display = checked ? 'block' : 'none';
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
  let extra = 0;
  let extraType = '';
  
  if (config.hasFine && document.getElementById('has-fine').checked) {
    extra = parseFloat(document.getElementById('fine-amount').value) || 0;
    extraType = 'fine';
  }
  if (config.hasIdFee && document.getElementById('has-id-fee').checked) {
    extra = parseFloat(document.getElementById('id-fee').value) || 0;
    extraType = 'id_fee';
  }
  
  selectedProcesses.push({
    name: processName,
    amount: amount,
    extra: extra,
    extraType: extraType
  });
  
  // Reset form
  select.value = '';
  amountInput.value = '';
  document.getElementById('special-fields').style.display = 'none';
  document.getElementById('has-fine').checked = false;
  document.getElementById('has-additional').checked = false;
  document.getElementById('fine-amount').value = '';
  document.getElementById('additional-amount').value = '';
  document.getElementById('fine-amount').style.display = 'none';
  document.getElementById('additional-amount').style.display = 'none';
  
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
    let total = p.amount + p.extra;
    let extraLabel = '';
    if (p.extra > 0) {
      extraLabel = p.extraType === 'fine' ? ` (+AED ${p.extra} fine)` : ` (+AED ${p.extra})`;
    }
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
  selectedProcesses.forEach(p => total += p.amount + p.extra);
  
  document.getElementById('total-display').textContent = `AED ${total.toLocaleString()}`;
  document.getElementById('proc-count').textContent = selectedProcesses.length;
  document.getElementById('proc-subtotal').textContent = `AED ${total.toLocaleString()}`;
}

async function saveRecord() {
  const company = document.getElementById('record-company').value.trim();
  const clientName = document.getElementById('record-client-name').value.trim();
  const phone = document.getElementById('record-phone').value.trim();
  
  if (!company) {
    showToast('Please enter or select a company', 'warning');
    return;
  }
  if (!clientName) {
    showToast('Please enter client name', 'warning');
    return;
  }
  if (selectedProcesses.length === 0) {
    showToast('Please add at least one process', 'warning');
    return;
  }
  
  // Build process data
  const processes = selectedProcesses.map(p => {
    const data = { name: p.name, amount: p.amount };
    if (p.extra > 0) {
      if (p.extraType === 'fine') data.fine = p.extra;
      else if (p.extraType === 'id_fee') data.id_fee = p.extra;
      else data.additional = p.extra;
    }
    return data;
  });
  
  const totalAmount = selectedProcesses.reduce((sum, p) => sum + p.amount + p.extra, 0);
  
  try {
    const result = await eel.save_record(company, clientName, phone, processes, totalAmount)();
    if (result.success) {
      showToast('Record saved successfully');
      clearRecordForm();
    } else {
      showToast(result.error || 'Failed to save record', 'error');
    }
  } catch (e) {
    showToast('Error saving record', 'error');
    console.error(e);
  }
}

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
   UTILITIES
═══════════════════════════════════════════════════════════════ */

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  loadDashboard();
  
  // Company search functionality
  const searchInput = document.getElementById('company-search');
  if (searchInput) {
    searchInput.addEventListener('input', filterCompanyRecords);
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
