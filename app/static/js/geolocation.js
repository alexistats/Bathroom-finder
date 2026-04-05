/**
 * geolocation.js
 * Handles "Find Bathrooms Near Me" button: gets user coordinates via browser API,
 * queries /api/bathrooms with lat/lon, then renders a sorted nearby list.
 */

let userMarker = null;
let radiusCircle = null;
let leafletMap = null;

function getLeafletMap() {
  // Folium embeds the Leaflet map inside an iframe; for same-origin embeds
  // we work directly with the global L object if Folium rendered inline.
  // If the map is in the iframe, we read the iframe's window.
  if (leafletMap) return leafletMap;

  // Folium renders the map div with id starting with "map_"
  const mapDivs = document.querySelectorAll('[id^="map_"]');
  if (mapDivs.length > 0) {
    // The Leaflet map object is stored on the DOM element
    const mapId = mapDivs[0].id;
    if (window[mapId]) {
      leafletMap = window[mapId];
      return leafletMap;
    }
  }
  return null;
}

function locateMe() {
  const status = document.getElementById('locate-status');
  const btn = document.getElementById('btn-locate');

  if (!navigator.geolocation) {
    status.textContent = 'Geolocation is not supported by your browser.';
    return;
  }

  btn.disabled = true;
  status.textContent = 'Getting your location…';

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      status.textContent = '';
      fetchNearby(lat, lon);
    },
    (err) => {
      btn.disabled = false;
      const messages = {
        1: 'Location access denied. Please allow location access in your browser.',
        2: 'Location unavailable. Try again.',
        3: 'Location request timed out.',
      };
      status.textContent = messages[err.code] || 'Could not get location.';
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
  );
}

function fetchNearby(lat, lon) {
  const radiusKm = document.getElementById('filter-radius')?.value || 5;
  const accessible = document.getElementById('filter-accessible')?.checked ? '&accessible=true' : '';
  const gender = document.getElementById('filter-gender')?.value || '';
  const genderParam = gender ? `&gender=${gender}` : '';

  const url = `/api/bathrooms?lat=${lat}&lon=${lon}&radius=${radiusKm}${accessible}${genderParam}`;

  fetch(url)
    .then(r => r.json())
    .then(data => {
      renderNearbyList(data);
      placeUserOnMap(lat, lon, parseFloat(radiusKm));
      document.getElementById('btn-locate').disabled = false;
      const status = document.getElementById('locate-status');
      status.textContent = data.length > 0
        ? `${data.length} bathroom${data.length !== 1 ? 's' : ''} within ${radiusKm} km`
        : `No bathrooms within ${radiusKm} km`;
    })
    .catch(() => {
      document.getElementById('btn-locate').disabled = false;
      document.getElementById('locate-status').textContent = 'Error fetching nearby bathrooms.';
    });
}

function renderNearbyList(bathrooms) {
  const list = document.getElementById('nearby-list');
  if (!list) return;

  if (bathrooms.length === 0) {
    list.innerHTML = '<p class="small text-muted mt-1">No bathrooms found nearby.</p>';
    return;
  }

  list.innerHTML = bathrooms.map(b => {
    const overall = b.ratings?.avg_overall || 0;
    const stars = '★'.repeat(Math.round(overall)) + '☆'.repeat(5 - Math.round(overall));
    const access = b.accessibility ? '♿ ' : '';
    return `
      <div class="nearby-item">
        <a href="/bathroom/${b.id}" class="fw-semibold text-decoration-none">${b.name}</a>
        <div class="small text-muted">${access}${b.distance_label || ''}</div>
        <div class="small" style="color:#f5a623">${stars}</div>
      </div>`;
  }).join('');
}

function placeUserOnMap(lat, lon, radiusKm) {
  const map = getLeafletMap();
  if (!map) return;

  if (userMarker) {
    map.removeLayer(userMarker);
  }
  if (radiusCircle) {
    map.removeLayer(radiusCircle);
  }

  userMarker = L.marker([lat, lon], {
    icon: L.divIcon({
      className: '',
      html: '<div style="background:#0d6efd;width:14px;height:14px;border-radius:50%;border:3px solid white;box-shadow:0 0 6px rgba(0,0,0,0.4)"></div>',
      iconSize: [14, 14],
      iconAnchor: [7, 7],
    }),
  }).bindTooltip('You are here').addTo(map);

  radiusCircle = L.circle([lat, lon], {
    radius: radiusKm * 1000,
    color: '#0d6efd',
    fillColor: '#0d6efd',
    fillOpacity: 0.05,
    weight: 1.5,
  }).addTo(map);

  map.setView([lat, lon], 14);
}

function applyFilters() {
  // Re-trigger nearby fetch if we already have a position cached
  if (window._lastLat && window._lastLon) {
    fetchNearby(window._lastLat, window._lastLon);
  }
}

// Cache coordinates for filter changes
const _origFetchNearby = fetchNearby;
function fetchNearby(lat, lon) {
  window._lastLat = lat;
  window._lastLon = lon;
  _origFetchNearby(lat, lon);
}
