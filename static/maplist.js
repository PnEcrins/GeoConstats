let selectedTr;
let selectedLayer;
let geojsonLayer;

function selectMapConstat(idConstat) {
    console.log("id_constat", idConstat);
    if(selectedTr) {
        selectedTr.style["background-color"] = 'white';
    };
    if(selectedLayer) {
        selectedLayer.setStyle({"color": "#3388ff"});
    }
    for (let id in geojsonLayer._layers) {
        layer = geojsonLayer._layers[id];
        console.log(layer.feature.properties);
        if(idConstat == layer.feature.properties.id_constat) {
            selectedLayer = layer;
            layer.setStyle({"color": "red"});
        }
    }
}
function onEachFeature(feature, layer) {
    layer.bindPopup(
        "<a href='constat/"+feature.properties.id_constat+"'> Voir la fiche </a> "
    )
    layer.on({
        click: function(e) {
            if(selectedTr) {
                selectedTr.style["background-color"] = 'white'
                selectedTr = null;
            };
            if(selectedLayer) {
                selectedLayer.setStyle({"color": "#3388ff"});
            }
            selectedLayer = layer;
            selectedLayer.setStyle({"color": "red"});
            selectedTr = document.getElementById("constat_"+feature.properties.id_constat);
            selectedTr.scrollIntoView();
            selectedTr.style["background-color"] = '80FF00';
        }
    })
}

// CONFIGURATION DE LA CARTE //
var map = L.map('map').setView([44.8, 6.2], 10);
L.tileLayer('https://a.tile.opentopomap.org/{z}/{x}/{y}.png', {
attribution: 'Map data: &copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors, SRTM | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (CC-BY-SA)'
}).addTo(map); 
// ACTIONS SUR LA CARTE
function changeZoom() {
    map.setZoom(10);
    map.setView([44.8, 6.2]);   
};
geojsonLayer = L.geoJSON(
    geojson, 
    {
        pointToLayer: function (feature, latlng) {
            return L.circleMarker(latlng);
        },
        onEachFeature : onEachFeature
    }
)
geojsonLayer.addTo(map);