let selectedTr;
let selectedLayer;
let geojsonLayer;



function selectMapConstat(idConstat) {
    if(selectedTr) {
        selectedTr.style["background-color"] = 'white';
    };
    for (let id in geojsonLayer._layers) {
        layer = geojsonLayer._layers[id];
        console.log(layer.feature.properties);
        if(idConstat == layer.feature.properties.id_constat) {
            selectedLayer = layer;
            layer.openPopup()
            map.setView(layer.getLatLng(), 13)
        }
    }
}

function getColor(statut) {
    switch (statut) {
        case 1:
            return "black"
        case 2:
            return "red"
        case 3:
            return "green"

    }  
}

function onEachFeature(feature, layer) {
    var statusColor = getColor(feature.properties.statut);
    if (feature.properties.declaratif ){
        layer.setStyle({
            color: statusColor,
            weight: 3,
            opacity: 1,
            fillOpacity: 0,
        })
    } else {
        layer.setStyle({
            fillColor: statusColor,
            color: statusColor,
            weight: 1,
            opacity: 1,
            fillOpacity: 1,
        })
    }
    if(feature.properties.statut_rel) {
        layer.bindPopup(
            "<b> Statut : </b>"+ feature.properties.statut_rel.nom+" <br/>\
            <a href='constat/"+feature.properties.id_constat+"'> Voir la fiche </a>\
            "
        )
    }
    layer.on({
        click: function(e) {
            if(selectedTr) {
                selectedTr.style["background-color"] = 'white'
                selectedTr = null;
            };
            selectedLayer = layer;
            selectedLayer.openPopup()
            selectedTr = document.getElementById("constat_"+feature.properties.id_constat);
            selectedTr.scrollIntoView();
            selectedTr.style["background-color"] = '80FF00';
        }
    })
}

// CONFIGURATION DE LA CARTE //


var legendControl = L.control();
legendControl.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'legend-info'); // create a div with a class "info"
    this.update();
    return this._div;
};

legendControl.update = function () {
    this._div.innerHTML = `
     <span class="line green"> </span>Indemnisé  <br> 
     <span class="line red"> </span>Rejeté  <br> 
     <span class="line black"> </span>En attente  <br> <br> 
     <span class="circle fullfill"> </span> Constat  <br> 
     <span class="circle"> </span> Constat déclaratif  <br> 
     `
};

legendControl.addTo(map);


var layerFeatureGroup = L.featureGroup([]).addTo(map);

geojsonLayer = L.geoJSON(
    geojson, 
    {
        pointToLayer: function (feature, latlng) {
            return L.circleMarker(latlng);
        },
        onEachFeature : onEachFeature
    }
)

layerFeatureGroup.addLayer(geojsonLayer);
layerFeatureGroup.bringToFront();
