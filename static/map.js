var map = L.map('map').setView([44.8, 6.2], 10);
var mainTileLayer = L.tileLayer('https://a.tile.opentopomap.org/{z}/{x}/{y}.png', {
attribution: 'Map data: &copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors, SRTM | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (CC-BY-SA)'
})
mainTileLayer.addTo(map); 

var backgroundFeatureGroup = L.featureGroup([], {"pane": "tilePane"}).addTo(map);

// function onEachFeatureLayer(feature, layer) {
//     layer.on('contextmenu', e => {
//           layer.bindPopup(`${feature.properties}`);
//           layer.openPopup();
//       }); 
// }

fetch(urlAreas+"?area_type_code=AA").then(function(resp) {
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

fetch(urlAreas+"?area_type_code=ZC").then(function(resp) {
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
fetch(urlAreas+"?area_type_code=ALPAGES_ZP").then(function(resp) {
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

fetch(urlAreas+"?area_type_code=ALPAGES_UP").then(function(resp) {
    return resp.json()
    }).then(function(geojson) {
        backgroundFeatureGroup.addLayer(
            L.geoJSON(
                geojson,
                {
                    "style": function(feature) {
                        return {
                            color: "#ff2200",
                            fillOpacity: 0
                        }
                    }
                }
            )
        );
        backgroundFeatureGroup.bringToBack();
});