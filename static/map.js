var map = L.map('map').setView([44.8, 6.2], 10);
var mainTileLayer = L.tileLayer(
"https://data.geopf.fr/private/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&apikey=ign_scan_ws&LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS&EXCEPTIONS=text/xml&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&FORMAT=image/jpeg&STYLE=normal"
, {"attribution": "&copy IGN"}
)
mainTileLayer.addTo(map); 

var backgroundFeatureGroup = L.featureGroup([], {"pane": "tilePane"}).addTo(map);



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
                            fillOpacity: 0,
                            weight:2
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
                            fillOpacity: 0,
                            weight:1
                        }
                    }
                }
            )
        );
        backgroundFeatureGroup.bringToBack();
});
