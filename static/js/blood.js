/* Blood availability search with alternatives */

async function searchBlood() {
  const bloodGroup = document.getElementById('blood_group')?.value;
  const quantity = document.getElementById('quantity')?.value;
  const location = document.getElementById('location')?.value || '';
  const results = document.getElementById('blood-results');
  if (!results) return;
  results.innerHTML = '<div class="empty-state">Searching...</div>';
  try {
    const params = new URLSearchParams({ blood_group: bloodGroup, quantity, location });
    const data = await apiFetch(`/api/blood/search?${params}`);
    const payload = data.data;
    if (payload.available && payload.results.length) {
      results.innerHTML = renderBloodTable(payload.results, 'Available Blood');
    } else {
      let html = `<div class="alert alert-error">${payload.message || 'Blood is not available at this location.'}</div>`;
      if (payload.alternatives && payload.alternatives.length) {
        html += '<h3 style="margin:1rem 0 0.5rem;color:var(--primary-dark);">Alternative Blood Banks</h3>';
        html += renderBloodTable(payload.alternatives, null);
      } else {
        html += '<div class="empty-state">No alternative blood banks found.</div>';
      }
      results.innerHTML = html;
    }
  } catch (err) {
    results.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
  }
}

function renderBloodTable(items) {
  let html = `<div class="table-wrap"><table class="data"><thead>
    <tr><th>Blood Group</th><th>Qty</th><th>Blood Bank</th><th>Hospital</th><th>Location</th><th>Contact</th><th>Updated</th></tr>
    </thead><tbody>`;
  items.forEach((s) => {
    html += `<tr>
      <td><strong>${s.blood_group}</strong></td>
      <td>${s.available_quantity} ${s.unit || 'Units'}</td>
      <td>${s.blood_bank_name || '-'}</td>
      <td>${s.hospital || '-'}</td>
      <td>${s.location || '-'}</td>
      <td>${s.phone || '-'}</td>
      <td>${s.last_updated ? s.last_updated.replace('T', ' ').slice(0, 16) : '-'}</td>
    </tr>`;
  });
  html += '</tbody></table></div>';
  return html;
}
