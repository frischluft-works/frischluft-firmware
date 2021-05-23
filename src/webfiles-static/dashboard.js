STATUS_INTERVAL_MS = 10000; // Get the status all X milliseconds

window.CHART_SHOW_ONLY_PPM = true;

// Divs
const DIV_LOADING = document.getElementById('loading');
const DIV_DASHBOARD = document.getElementById('dashboard');
const DIV_CHART = document.getElementById('chart');
const DIV_DEVTOOLS = document.getElementById('devtools');

const dashboardCurrentValue = document.getElementById('current-value');
const dashboardPastValues = document.getElementById('past-values');

let dataIntervalSec = 0; // Is fetched from device through getStatus

// KeyPress handler
document.onkeypress = (e) => {
  // x: show all sensor values
  if (e.key === 'x' || e.key === 'i') {
    toggleDevtools();
  } else if (e.key === 'p') {
    addDummyPpm();
  }
};

// Helper for HTML
const isHidden = (el) => el.offsetParent === null;

// Start requesting status updates
getStatus();

let lastStatus = null; // last received satus
let chartIsSetup = false;

// Main code functions after here
function initCharts() {
  // Chart code, if we could load highcharts over internet
  if (!window.Highcharts) {
    // offline mode
    dashboardPastValues.style.display = 'flex';
  } else {
    console.log('Highcharts');
    dashboardPastValues.style.display = 'none';
    DIV_CHART.style.display = 'block';

    Highcharts.setOptions({
      time: {
        useUTC: false,
        /*
        getTimezoneOffset: function (timestamp) {
            var zone = 'Europe/Oslo',
            timezoneOffset = -moment.tz(timestamp, zone).utcOffset();

            return timezoneOffset;
        }
    */
      },
    });

    window.chart = Highcharts.chart('container', {
      title: {
        text: null,
      },
      xAxis: {
        type: 'datetime',
        // tickPixelInterval: 150
        dateTimeLabelFormats: {
          minute: '%H:%M',
        },
      },
      yAxis: [
        {
          title: { text: 'ppm' },
          zIndex: 100,
          lineWidth: 3,
          min: 400,
          max: 2100,

          plotLines: [{
            value: 410,
            color: 'green',
            dashStyle: 'shortdash',
            width: 2,
            label: {
              text: 'Außenluft',
            },
          },
          {
            value: lastStatus.thresholdWarningPpm,
            color: 'yellow',
            dashStyle: 'shortdash',
            width: 2,
            label: {
              text: 'Bis hier OK, ab hier lüften',
            },
          },
          {
            value: lastStatus.thresholdAlertPpm,
            color: 'red',
            dashStyle: 'shortdash',
            width: 2,
            label: {
              text: 'CO2 VIEL zu hoch!',
            },
          },
          ],
        },


        { // Temperature yAxis
          gridLineWidth: 0,
          title: false,
          labels: {enabled:false}

        },


        { // Humidity yAxis
          gridLineWidth: 0,
          title: false,
          labels: {enabled:false}
        },

        { // Pressure yAxis
          gridLineWidth: 0,
          title: false,
          labels: {enabled:false}
        },

      ],
      plotOptions: {
        series: {
          label: {
            connectorAllowed: false,
          },
        },
      },
      tooltip: {
        shared: true,
        //split: false,
        //enabled: true,

        dateTimeLabelFormats: {
          millisecond: '%H:%M',
        },
      },
      series: [{
        name: 'PPM',
        yAxis: 0,
        //  type: 'column',

      },
      {
        name: 'Temperature',
        yAxis: 1,
        lineWidth: 0,
        marker: {enabled:false}
  

      },
      {
        name: 'Humidity',
        yAxis: 2,
        lineWidth: 0,
        marker: {enabled:false}
      },
      {
        name: 'Pressure',
        yAxis: 3,
        lineWidth: 0,
        marker: {enabled:false}
      }
      ],
    });
  };
}


function updateData(dataBuffers) {
  const ppmArr = dataBuffers.ppm;
  const tempArr = dataBuffers.temp;
  const humidityArr = dataBuffers.humidity;
  // console.log('ppmArr', ppmArr);


  const lastPpm = ppmArr[ppmArr.length - 1];
  dashboardCurrentValue.innerHTML = lastPpm + ' ppm';


  // Only proceed if Highchart is available
  if (!window.chart) return;

  const startTime = (new Date()).getTime();
  const create_series_datapoint_with_time = (dataArr) => {
    // Reduce the current time used for net datapoint by 1 minute:
    const seriesData = [];
    let curTime = startTime;
    for (const value of dataArr.reverse()) {
      seriesData.push([curTime, value]);
      curTime -= dataIntervalSec * 1000; // new entry every minute
    }
    return seriesData.reverse()
  }

  window.chart.series[0].setData(create_series_datapoint_with_time(ppmArr));
  window.chart.series[1].setData(create_series_datapoint_with_time(tempArr));
  window.chart.series[2].setData(create_series_datapoint_with_time(humidityArr));
}

function updateDevInfo(sysInfo) {
  const data = {
    memFree: sysInfo.memFree,
    uname: sysInfo.uname,
    fs: {
      blockSize: sysInfo.fsInfo[0],
      blocksTotal: sysInfo.fsInfo[2],
      blocksFree: sysInfo.fsInfo[3],
    },

  };
  DIV_DEVTOOLS.innerHTML = `<pre>${JSON.stringify(data, null, 4)}</pre>`;
}





var nameSet = false;

function getStatus() {
  fetch('/status')
    .then((response) => response.json())
    .then((data) => {
      lastStatus = data;
      console.log(lastStatus);

      DIV_LOADING.style.display = 'none';
      DIV_DASHBOARD.style.display = 'block';

      if (!chartIsSetup) {
        initCharts();
        chartIsSetup = true;
      }


      if (!nameSet) {

        console.log("setting name");
        if (data.sysInfo.deviceName) {
          newTitle = "🚦 Frischluft.works - " + data.sysInfo.deviceName

          console.log(newTitle);

          document.getElementById('nameHeader').innerHTML = newTitle;
          document.title = newTitle;
        }
        nameSet = true;
      }


      // Update chart
      dataIntervalSec = data.dataInterval;
      updateData(data.dataBuffers);
      updateDevInfo(data.sysInfo);

      // check again soon
      setTimeout(getStatus, STATUS_INTERVAL_MS);
    })
    .catch((err) => {
      console.error(err);
      // eslint-disable-next-line no-unused-vars
      setTimeout(getStatus, STATUS_INTERVAL_MS);
    });
}

function addDummyPpm() {
  // Create new series data with one additional, random point
  const ppm = window.chart.series[0].options.data.map((dp) => dp[1]); // filter out existing timestamps, get just the raw values array
  const temp = window.chart.series[1].options.data.map((dp) => dp[1]); // filter out existing timestamps, get just the raw values array
  const humidity = window.chart.series[2].options.data.map((dp) => dp[1]); // filter out existing timestamps, get just the raw values array

  // Add a new value
  ppm.push(parseInt(Math.random() * 2000, 10));
  temp.push(parseInt(Math.random() * 50, 10));
  humidity.push(parseInt(Math.random() * 100, 10));

  // Update the chart
  const databuffer = { ppm, temp, humidity }
  updateData(databuffer);
}

function toggleDevtools() {
  console.log('toggle');
  if (isHidden(DIV_DEVTOOLS)) {
    DIV_DEVTOOLS.style.display = 'block';
  } else {
    DIV_DEVTOOLS.style.display = 'none';
  }
}
