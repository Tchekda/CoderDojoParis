let iconFeatures = [],
    coord = [2.33131, 48.87301],
    iconFeature = new ol.Feature({
        geometry: new ol.geom.Point(ol.proj.transform(coord, 'EPSG:4326',
            'EPSG:3857')),
        name: 'CoderDojo Paris',
    });

iconFeatures.push(iconFeature);

let vectorSource = new ol.source.Vector({
        features: iconFeatures //add an array of features
    }),
    iconStyle = new ol.style.Style({
        image: new ol.style.Icon(({
            anchor: [0.5, 46],
            anchorXUnits: 'fraction',
            anchorYUnits: 'pixels',
            opacity: 0.75,
            scale: 0.2,
            src: logourl
        }))
    }),

    vectorLayer = new ol.layer.Vector({
        source: vectorSource,
        style: iconStyle
    });

map = new ol.Map({
    target: 'osmMap',
    layers: [
        new ol.layer.Tile({
            source: new ol.source.OSM()
        }),
        vectorLayer
    ],
    view: new ol.View({
        center: ol.proj.fromLonLat(coord),
        zoom: 16
    })
});