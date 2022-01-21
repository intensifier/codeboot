const codebootCharts = (function () {
  const vegaLiteOptions = {
    config: {
    },
    init: (view) => {
      view.tooltip(new vegaTooltip.Handler().call);
    },
    view: {
      renderer: "canvas",
    },
  };

  // register vega and vega-lite with the API
  vl.register(vega, vegaLite, vegaLiteOptions);

  function drawLine(csv, xDesc, yDesc) {
    var chart = document.getElementsByClassName('cb-html-window')[0];

    var data = csv_to_vega(csv);

    var xField, xTooltip, xLabel, xType;
    var yField, yTooltip, yLabel, yType;

    [xLabel, xType] = xDesc.split(':');
    [yLabel, yType] = yDesc.split(':');

    if (xType === "unix_timestamp") {
      // Scale to 1000x
      data.forEach(e => {
        e[xLabel] = 1000 * e[xLabel];
      })

      xField = vl.x().fieldT(xLabel);
      xTooltip = vl.fieldT(xLabel);
    } else {
      xField = vl.x().fieldQ(xLabel);
      xTooltip = vl.fieldQ(xLabel);
    }

    // TODO: Handle yType
    yField = vl.y().fieldQ(yLabel);
    yTooltip = vl.fieldQ(yLabel);

    // Clear the last chart
    chart.innerHTML = "";

    vl.markLine({ tooltip: true })
      .data(data)
      .encode(
        xField,
        yField,
        vl.tooltip([xTooltip, yTooltip])
      )
      .render()
      .then(viewElement => {
        chart.appendChild(viewElement);
      });

  }

  function csv_to_vega(csv) {
    var _csv = csv.split('\n');
    var cols = _csv[0].split(',');

    var rows = [];
    _csv.slice(1).forEach(row => {
      _row = row.split(',');
      var d = {};
      cols.forEach((field, i) => {
        d[field] = Number(_row[i]);
      });
      rows.push(d);
    })
    return rows;
  }

  return {
    csv_to_vega,
    drawLine
  }
})();
