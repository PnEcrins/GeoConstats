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
 
    layer.bindPopup(
        "<b> Statut : </b>"+ feature.properties.statut_rel.nom+" <br/>\
        <a href='constat/"+feature.properties.id_constat+"'> Voir la fiche </a>\
        "
    )
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
var map = L.map('map').setView([44.8, 6.2], 10);
L.tileLayer('https://a.tile.opentopomap.org/{z}/{x}/{y}.png', {
attribution: 'Map data: &copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors, SRTM | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (CC-BY-SA)'
}).addTo(map); 

var legendControl = L.control();
legendControl.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'legend-info'); // create a div with a class "info"
    this.update();
    return this._div;
};

legendControl.update = function () {
    this._div.innerHTML = `
     <span class="line green"> </span>Accepté  <br> 
     <span class="line red"> </span>Rejeté  <br> 
     <span class="line black"> </span>En attente  <br> <br> 
     <span class="circle"> </span> Constat déclaratif  <br> 
     <span class="circle fullfill"> </span> Constat non déclaratif  <br> 
     `
};

legendControl.addTo(map);


var layerFeatureGroup = L.featureGroup([]).addTo(map);
var backgroundFeatureGroup = L.featureGroup([], {"pane": "tilePane"}).addTo(map);
// ACTIONS SUR LA CARTE
function changeZoom() {
    map.setZoom(10);
    map.setView([44.8, 6.2]);   
};
fetch("areas/AA").then(function(resp) {
    return resp.json()
    }).then(function(geojson) {
        backgroundFeatureGroup.addLayer(
            L.geoJSON(
                geojson,
                {
                    "style": function(feature) {
                        return {
                            color: "#341354",
                            fillOpacity: 0,
                            dashArray: "10 10"
                        }
                    }
                }
            )
        );
        backgroundFeatureGroup.bringToBack();
})

fetch("areas/ZC").then(function(resp) {
    return resp.json()
    }).then(function(geojson) {
        backgroundFeatureGroup.addLayer(
            L.geoJSON(
                geojson,
                {
                    "style": function(feature) {
                        return {
                            color: "#341354",
                            fillOpacity: 0
                        }
                    }
                }
            )
        );
        backgroundFeatureGroup.bringToBack();
});

fetch("areas/ALPAGES").then(function(resp) {
    return resp.json()
    }).then(function(geojson) {
        backgroundFeatureGroup.addLayer(
            L.geoJSON(
                geojson,
                {
                    "style": function(feature) {
                        return {
                            color: "#ff8200",
                            fillOpacity: 0
                        }
                    }
                }
            )
        );
        backgroundFeatureGroup.bringToBack();
});


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
geojsonLayer.bringToFront();