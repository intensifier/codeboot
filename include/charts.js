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

  function drawLine(csv, xLabel, yLabel, xType) {
    var chart = document.getElementsByClassName('cb-html-window')[0];

    var data = csv_to_vega(csv);

    // Clear the last chart
    chart.innerHTML = "";

    if (xType === 'timestamp') {
      xField = vl.x().fieldT(xLabel);
    } else {
      xField = vl.x().fieldQ(xLabel);
    }

    vl.markLine({ tooltip: true })
      .data(data)
      .encode(
        xField,
        vl.y().fieldQ(yLabel),
        vl.tooltip([vl.fieldQ(xLabel), vl.fieldQ(yLabel)])
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
