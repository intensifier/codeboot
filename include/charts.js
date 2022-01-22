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

  function plot(data, markType, title, xDesc, yDesc, zDesc) {
    var chart = document.getElementsByClassName('cb-html-window')[0];

    var _data = list_conv(data);

    // Handle chart type
    var mark;

    if (markType === "line") {
      mark = vl.markLine;
    } else if (markType === "bar") {
      mark = vl.markBar;
    } else if (markType === "point") {
      mark = vl.markPoint;
    }

    // Handle axis types
    var xField, xTooltip, xLabel, xType;
    var yField, yTooltip, yLabel, yType;
    var zField, zTooltip, zLabel, zType;

    [xLabel, xType] = xDesc.split(':');
    [yLabel, yType] = yDesc.split(':');

    if (xType === "unix_timestamp") {
      // Scale to 1000x
      _data.forEach(e => {
        e[xLabel] = 1000 * e[xLabel];
      })

      xField = vl.x().fieldT(xLabel);
      xTooltip = vl.fieldT(xLabel);
    } else if (xType === "timestamp") {
      xField = vl.x().fieldT(xLabel);
      xTooltip = vl.fieldT(xLabel);
    }
    else {
      xField = vl.x().fieldQ(xLabel);
      xTooltip = vl.fieldQ(xLabel);
    }

    // TODO: Handle yType
    yField = vl.y().fieldQ(yLabel);
    yTooltip = vl.fieldQ(yLabel);

    // TODO: handle optional zType
    if (zDesc !== undefined) {
      [zLabel, zType] = zDesc.split(':');
      zField = vl.color().fieldN(zLabel);
      zTooltip = vl.fieldN(zLabel);
    }

    var encodeArgs;
    if (zDesc === undefined) {
      encodeArgs = [xField,
                    yField,
                    vl.tooltip([xTooltip, yTooltip])];
    } else {
      encodeArgs = [xField,
                    yField,
                    zField,
                    vl.tooltip([xTooltip, yTooltip, zTooltip])];
    }

    // Handle chart title
    if (title === undefined) {
      title = "";
    }

    // Clear the last chart
    chart.innerHTML = "";

    mark({ tooltip: true })
      .title(title)
      .data(_data)
      .encode(...encodeArgs)
      .render()
      .then(viewElement => {
        chart.appendChild(viewElement);
      });

    return 1;
  }

  function list_conv(data) {
    var cols = data[0];
    rows = [];
    data.slice(1).forEach(row => {
      var d = {};
      cols.forEach((e, i) => {
        d[e] = row[i];
      });
      rows.push(d);
    })
    return rows;
  }

  return {
    plot
  }
})();
