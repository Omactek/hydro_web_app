document.addEventListener("DOMContentLoaded", function() {
    const stationDropdown = document.getElementById("stationDropdown");
    const valueDropdown = document.getElementById("valueDropdown");
    const yearDropdown = document.getElementById("yearDropdown");
    const yearlyChart = document.getElementById("yearlyChart");
    const seriesChart = document.getElementById("seriesChart");
    const rangePicker = flatpickr('#rangePicker', {
        dateFormat: 'd.m.Y',
        minDate: '',
        maxDate: '',
        disable: [],
        defaultDate: [],
        mode: 'range',
    });

    function updateDatePicker(rangeWidget, startDate, endDate) {
        rangeWidget.set('minDate', startDate);
        rangeWidget.set('maxDate', endDate);
    };

    let stationsData = {};

    const map = L.map('map').setView([49.8175, 15.4730], 6); //centered on the Czech Republic

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, ' +
                 '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC BY-SA</a>'
    }).addTo(map);

    const markers = L.markerClusterGroup({ //using cluster plugin
        maxClusterRadius: 15,
        spiderfyDistanceMultiplier: 1.5,
        disableClusteringAtZoom: 16
    });

    const markerStyle = {
        radius: 6,
        fillColor: "#002f61", 
        color: "#000",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.7,
    };

    const highMarkerStyle = { //style for selected station marker
        radius: 6,
        fillColor: "#39be74",
        color: "#000",
        weight: 1,
        opacity: 1,
        fillOpacity: 1,
    };

    function zoomToStation(stationId) {
        const coordinates = stationsData[stationId];
        if (coordinates) {
            map.setView([coordinates[1], coordinates[0]], 16); //leaflet uses [lat, lng]
        }
    }

    function highlightMarker(stationId) {
        markers.eachLayer(function(layer) { //markers layer contains seperate layer for each marker
            if (layer.feature && layer.feature.id === stationId) {
                layer.setStyle(highMarkerStyle);
            } else {
                layer.setStyle(markerStyle);
            }
        });
    }

    fetch('/api/stations/geo/') //populating map layer
        .then(response => response.json())
        .then(data => {
            L.geoJSON(data, {
                pointToLayer: function(feature, latlng) {
                    const marker = L.circleMarker(latlng, markerStyle);
                    
                    marker.bindTooltip(feature.properties.st_label, {
                        sticky: true
                    });

                    marker.on('click', function() {
                        stationDropdown.value = feature.id;
                        fetchValues();
                        zoomToStation(feature.id);
                        highlightMarker(feature.id);
                    });

                    return marker;
                }
            }).addTo(markers); //each marker is added as seperate layer into this layer

            map.addLayer(markers);

            data.features.forEach(feature => { //store station data for later use
                stationsData[feature.id] = feature.geometry.coordinates;
            });
        })
        .catch(error => console.error('Error fetching GeoJSON data:', error));

    function formatDateForBackend(date) { //reformatting flat pickr date objects to be easily readable by back end view
        if (date) {
            const formattedDate = new Date(date);
            const year = formattedDate.getFullYear();
            const month = String(formattedDate.getMonth() + 1).padStart(2, '0'); //month is zero-based
            const day = String(formattedDate.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        }
        else {
            return '';
        }
    }

    function fetchStations() { //populating station dropdown
        fetch('/api/stations/')
            .then(response => response.json())
            .then(data => {
                stationDropdown.innerHTML = "";  //clears previous options
                data.forEach(station => {
                    const option = document.createElement("option");
                    option.value = station.st_name;
                    option.textContent = station.st_label;
                    stationDropdown.appendChild(option);
                });
                fetchValues();
            })
            .catch(error => console.error('Error fetching stations:', error));
    }

    function fetchValues() { //populating value dropdown
        const stationId = stationDropdown.value;
        fetch(`/api/stations/${stationId}/values/`)
            .then(response => response.json())
            .then(data => {
                valueDropdown.innerHTML = ""; 
                data.forEach(value => {
                    const option = document.createElement("option");
                    option.value = value.django_field_name;
                    option.textContent = value.parameter;
                    option.setAttribute('unit', value.unit); //store unit in data attribute
                    valueDropdown.appendChild(option);
                });
                fetchYears();
            })
            .catch(error => console.error('Error fetching values:', error));
    }

    function fetchYears() { //populating year dropdown
        const stationId = stationDropdown.value;
        fetch(`/api/stations/${stationId}/years/`)
            .then(response => response.json())
            .then(data => {
                yearDropdown.innerHTML = ""; 
                data.forEach(year => {
                    const option = document.createElement("option");
                    option.value = year;
                    option.textContent = year;
                    yearDropdown.appendChild(option);
                });
                fetchDataAndRenderYearlyChart();
                fetchDataAndRenderSeriesChart();
            })
            .catch(error => console.error('Error fetching years:', error));
    }

    function fetchDataAndRenderYearlyChart() {
        const stationId = stationDropdown.value;
        const valueField = valueDropdown.value;
        const year = yearDropdown.value;
        const parLabel = valueDropdown.options[valueDropdown.selectedIndex].textContent;
        const parUnit = valueDropdown.options[valueDropdown.selectedIndex].getAttribute('unit');

        // check if dropdowns have valid selections
        if (!stationId || !valueField || !year) return;

        fetch(`/api/stations/${stationId}/${valueField}/${year}/yearly-data/`)
            .then(response => response.json())
            .then(data => {
                const hourlyDates = data.map(item => item.date);
                const hourlyValues = data.map(item => item.value);

                fetch(`/api/stations/${stationId}/${valueField}/percentiles/`, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest' //custom header
                    }
                })
                    .then(response => response.json())
                    .then(percentiles => {
                        const currentYear = new Date(hourlyDates[0]).getFullYear();
                        const percDate = percentiles.map(d => `${currentYear}-${d.string_date_without_year}`);
                        const q10 = percentiles.map(d => d.q10);
                        const q20 = percentiles.map(d => d.q20);
                        const q30 = percentiles.map(d => d.q30);
                        const q40 = percentiles.map(d => d.q40);
                        const q50 = percentiles.map(d => d.q50);
                        const q60 = percentiles.map(d => d.q60);
                        const q70 = percentiles.map(d => d.q70);
                        const q80 = percentiles.map(d => d.q80);
                        const q90 = percentiles.map(d => d.q90);
                        const conTrace = {
                            x: percDate,
                            y:q50,
                            fill: 'None',
                            mode: 'lines',
                            line: {color: 'transparent'},
                            showlegend: false,
                            name: 'controll line',
                            hoverinfo: 'none',
                            connectgaps: true,
                        }
                        const conTrace2 = {
                            x: percDate,
                            y:q30,
                            fill: 'None',
                            mode: 'lines',
                            line: {color: 'transparent'},
                            showlegend: false,
                            name: 'controll line',
                            hoverinfo: 'none',
                            connectgaps: true,
                            legendgroup: 'Q30 to Q70'
                        }
                        const q10Trace = {
                            x: percDate,
                            y: q10,
                            line: {color: 'transparent'},
                            mode: "lines",
                            fill: 'tonexty',
                            fillcolor: 'rgba(0,100,80,0.2)', 
                            name: 'Q10',
                            type: 'scatter',
                            hoverinfo: 'y',
                            legendgroup: 'Q10 to Q90'
                        }
                        const q30Trace = {
                            x: percDate,
                            y: q30,
                            line: {color: 'transparent'},
                            mode: "lines",
                            fill: 'tonexty',
                            fillcolor: 'rgba(0,176,246,0.2)', 
                            name: 'Q30',
                            type: 'scatter',
                            hoverinfo: 'y',
                            legendgroup: 'Q30 to Q70'
                        }
                        const q70Trace = {
                            x: percDate,
                            y: q70,
                            line: {color: 'transparent'},
                            mode: "lines",
                            fill: 'tonexty',
                            fillcolor: 'rgba(0,176,246,0.2)', 
                            name: 'Q70',
                            type: 'scatter',
                            hoverinfo: 'y',
                            legendgroup: 'Q30 to Q70'
                        }
                        const q90Trace = {
                            x: percDate,
                            y: q90,
                            fill: 'tonexty',
                            fillcolor: 'rgba(0,100,80,0.2)', 
                            line: {color: 'transparent'},
                            mode: "lines",
                            name: 'Q90',
                            type: 'scatter',
                            hoverinfo: 'y',
                            legendgroup: 'Q10 to Q90'
                        }
                        const hourlyTrace = {
                            x: hourlyDates,
                            y: hourlyValues,
                            mode: 'lines',
                            name: 'Hourly Values',
                            line: {color: '#005f85'},
                            type: 'scatter',
                        };

                        const median = {
                            x: percDate,
                            y: q50,
                            mode: 'lines',
                            name: 'Median',
                            line: {color: '#f00069'},
                            hoverinfo: 'y',
                            connectgaps: true
                        };

                        const conTraceMed = {
                            x: percDate,
                            y:q50,
                            fill: 'None',
                            mode: 'lines',
                            line: {color: 'transparent'},
                            showlegend: false,
                            name: 'controll line',
                            hoverinfo: 'none',
                            connectgaps: true,
                        }
                        //control traces are needed due to plotly filling lines to next available line, this is why they are also uncluded in groups
                        const allTraces = [conTraceMed, conTrace2, q10Trace, conTrace, q30Trace, conTrace, median, q70Trace, q90Trace, hourlyTrace];
                        const layout = {
                            title: `Hourly data and monthly percentiles (all measured years)`,
                            xaxis: {
                                title: `date (${year})`,
                                type: 'date',
                                range: [`${currentYear}-01-01`, `${currentYear}-12-31`],
                            },
                            yaxis: {
                                title: `${parLabel} [${parUnit}]`
                            }
                        };
                        Plotly.newPlot(yearlyChart, allTraces, layout);
                })
            }
        )
        .catch(error => console.error('Error fetching chart data:', error));
    }

    function fetchDataAndRenderSeriesChart() { //also updates date picker with value range
        const stationId = stationDropdown.value;
        const valueField = valueDropdown.value;
        const startDate = rangePicker.selectedDates[0];
        const endDate = rangePicker.selectedDates[1];
        const parLabel = valueDropdown.options[valueDropdown.selectedIndex].textContent;
        const parUnit = valueDropdown.options[valueDropdown.selectedIndex].getAttribute('unit');

        const formattedStartDate = formatDateForBackend(startDate);
        const formattedEndDate = formatDateForBackend(endDate);

        if (!stationId || !valueField) return;
        fetch(`/api/stations/${stationId}/${valueField}/dataseries/?start=${formattedStartDate}&end=${formattedEndDate}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json())
            .then(responseData => {
                const minDate = responseData.min_date;
                const maxDate = responseData.max_date;
                const data = responseData.data;
                const hourlyDates = data.map(item => item.date);
                const hourlyValues = data.map(item => item.value);

                const hourlyTrace = {
                    x: hourlyDates,
                    y: hourlyValues,
                    mode: 'lines',
                    name: 'Hourly Values',
                    line: {color: '#005f85'},
                    type: 'scatter',
                    connectgaps: false
                };

                const layout = {
                    title: `Time series`,
                    xaxis: {
                        title: `date`,
                        type: 'date',
                    },
                    yaxis: {
                        title: `${parLabel} [${parUnit}]`
                    }
                };
                Plotly.newPlot(seriesChart, [hourlyTrace], layout);
                updateDatePicker(rangePicker, minDate, maxDate);
            }
        ).catch(error => console.error('Error fetching chart data:', error)); 
    }

    stationDropdown.addEventListener("change", function() {
        fetchValues();
        zoomToStation(stationDropdown.value);
        highlightMarker(stationDropdown.value);
        rangePicker.clear(); //more user friendly this way
    });

    function fetchDataAndRenderBothCharts() {
        fetchDataAndRenderYearlyChart();
        rangePicker.clear();
        fetchDataAndRenderSeriesChart();
    }

    valueDropdown.addEventListener("change", fetchDataAndRenderBothCharts);
    yearDropdown.addEventListener("change", fetchDataAndRenderYearlyChart);
    fetchStations();
    rangePicker.set('onChange', function() {
        if( rangePicker.selectedDates.length === 2) {
            fetchDataAndRenderSeriesChart();
        }
    });
});