/* Emergency hospital search with Geolocation API */

async function loadNearbyHospitals() {
  const results = document.getElementById('hospital-results');
  const statusEl = document.getElementById('geo-status');
  if (!results) return;

  function render(hospitals, note) {
    if (note && statusEl) statusEl.textContent = note;
    if (!hospitals.length) {
      results.innerHTML = '<div class="empty-state">No hospitals found.</div>';
      return;
    }
    let html = `<div class="table-wrap"><table class="data"><thead>
      <tr><th>Hospital</th><th>Address</th><th>City</th><th>Phone</th><th>Emergency</th><th>Distance</th><th>Services</th></tr>
      </thead><tbody>`;
    hospitals.forEach((h) => {
      html += `<tr>
        <td><strong>${h.name}</strong></td>
        <td>${h.address || '-'}</td>
        <td>${h.city || '-'}</td>
        <td><a href="tel:${h.phone || ''}">${h.phone || '-'}</a></td>
        <td><span class="badge ${h.emergency_available ? 'badge-success' : 'badge-danger'}">
          ${h.emergency_available ? 'Yes' : 'No'}</span></td>
        <td>${h.distance_km != null ? h.distance_km + ' km' : '-'}</td>
        <td>${h.services || '-'}</td>
      </tr>`;
    });
    html += '</tbody></table></div>';
    results.innerHTML = html;
  }

  async function fetchHospitals(lat, lon, q) {
    const params = new URLSearchParams();
    if (lat != null) params.set('lat', lat);
    if (lon != null) params.set('lon', lon);
    if (q) params.set('q', q);
    const data = await apiFetch(`/api/hospitals/emergency?${params}`);
    return data.data || [];
  }

  const manualQ = document.getElementById('hospital-search')?.value || '';

  if (!navigator.geolocation) {
    try {
      const hospitals = await fetchHospitals(null, null, manualQ);
      render(hospitals, 'Geolocation not supported. Showing all emergency hospitals.');
    } catch (err) {
      results.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
    }
    return;
  }

  if (statusEl) statusEl.textContent = 'Requesting location permission...';
  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      try {
        const hospitals = await fetchHospitals(pos.coords.latitude, pos.coords.longitude, manualQ);
        render(hospitals, `Location acquired (${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}). Sorted by distance.`);
      } catch (err) {
        results.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
      }
    },
    async () => {
      try {
        const hospitals = await fetchHospitals(null, null, manualQ);
        render(hospitals, 'Location permission denied. You can search hospitals manually.');
      } catch (err) {
        results.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
      }
    },
    { enableHighAccuracy: true, timeout: 10000 }
  );
}

async function manualHospitalSearch() {
  const q = document.getElementById('hospital-search')?.value || '';
  const results = document.getElementById('hospital-results');
  try {
    const params = new URLSearchParams({ q });
    const data = await apiFetch(`/api/hospitals/emergency?${params}`);
    const hospitals = data.data || [];
    if (!hospitals.length) {
      results.innerHTML = '<div class="empty-state">No hospitals match your search.</div>';
      return;
    }
    let html = `<div class="table-wrap"><table class="data"><thead>
      <tr><th>Hospital</th><th>Address</th><th>City</th><th>Phone</th><th>Emergency</th><th>Services</th></tr>
      </thead><tbody>`;
    hospitals.forEach((h) => {
      html += `<tr>
        <td><strong>${h.name}</strong></td>
        <td>${h.address || '-'}</td>
        <td>${h.city || '-'}</td>
        <td>${h.phone || '-'}</td>
        <td>${h.emergency_available ? 'Yes' : 'No'}</td>
        <td>${h.services || '-'}</td>
      </tr>`;
    });
    html += '</tbody></table></div>';
    results.innerHTML = html;
  } catch (err) {
    results.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
  }
}
