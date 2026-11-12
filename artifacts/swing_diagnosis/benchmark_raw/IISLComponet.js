var trHtml = "";
function Nifty50home() {
    var b = null,
        c = null,
        d = null;
    return (
        $.ajax({
            type: "GET",
            url: "https://liveindexsa.niftyindices.com/jsonfiles/LiveIndicesWatch.json",
            data: "{}",
            async: !0,
            cache: !1,
            dataType: "json",
            success: function (e) {
                if ("" == e) isSuccess = !1;
                else
                    for (var f = e, g = 0; g < f.data.length; g++) {
                        "NIFTY 50" == f.data[g].indexName &&
                            ($("#nifty50Val").html(f.data[g].last),
                                (b = f.data[g].last),
                                (perchange = f.data[g].percChange),
                                (b = b.replace(/\,/g, "")),
                                (b = parseFloat(b)),
                                $("#nifty50Pchangeval").html(f.data[g].percChange + "%"),
                                $("#ABC").html(perchange),
                                perchange > 0
                                    ? ($("#nifty50Pchangeval").removeClass("redpercentage"), $("#nifty50Pchangeval").addClass("greenpercentage"))
                                    : ($("#nifty50Pchangeval").removeClass("greenpercentage"), $("#nifty50Pchangeval").addClass("redpercentage")),
                                (d = f.data[g].previousClose),
                                (d = d.replace(/\,/g, "")),
                                (d = parseFloat(d)),
                                (c = b - d),
                                $("#nifty50Changeval").html(c.toFixed(2)),
                                c > 0 ? ($("#nifty50Changeval").removeClass("redvalue"), $("#nifty50Changeval").addClass("greenvalue")) : ($("#nifty50Changeval").removeClass("greenvalue"), $("#nifty50Changeval").addClass("redvalue"))),
                            (isSuccess = !0);
                        break;
                    }
            },
            error: function (a) { },
        }),
        !1
    );
}
function initCMintraday(a, b) {
    b = b.replace("&amp;", "&");
    $.ajax({
        type: "GET",
        url: "https://liveindexsa.niftyindices.com/jsonfiles/CMIntraday/CMIntraday" + b + ".json",
        data: "{}",
        async: !1,
        cache: !1,
        dataType: "json",
        success: function (b) {
            if (b != null) {
                callloadchartCMIntraday(a, b), loaderhide();
            }
        },
        error: function (a) {
            loaderhide();
        },
    });
}
function initintraday(a, b) {
    b = b.toUpperCase().trim();
    $.ajax({
        type: "GET",
        url: "https://liveindexsa.niftyindices.com/jsonfiles/Intraday/Intraday" + b + ".json",
        data: "{}",
        async: !1,
        cache: !1,
        dataType: "json",
        success: function (b) {
            if (b != null) {
                callloadchartIntraday(a, b), loaderhide();
            }
        },
        error: function (a) {
            loaderhide();
        },
    });
}
function callloadchartCMIntraday(a, b) {
    var c = [],
        d = [];
    $.each(b.graphData[0].data, function (a, b) {
        var e = b.time.substring(11);
        (c[a] = [e, Number(b.close)]), (d[a] = b.close);
    });
    var e = Math.min.apply(null, d),
        f = Math.max.apply(null, d);
    loadAreaChart(a, c, e, f);
}
function callloadchartIntraday(a, b) {
    var c = [],
        d = [];
    $.each(b.graphData, function (a, b) {
        var e = b.time.substring(11);
        (c[a] = [e, Number(b.close)]), (d[a] = b.close);
    });
    var e = Math.min.apply(null, d),
        f = Math.max.apply(null, d);
    loadAreaChart(a, c, e, f);
}
function loadAreaChart(a, b, c, d) {
    console.log(a);
    Highcharts.setOptions({ colors: ["#b2f2ff"] });
    var e = new Highcharts.Chart({
        legend: !1,
        chart: { renderTo: a, type: "area", backgroundColor: "rgba(0,0,0,0)" },
        title: { text: "" },
        plotOptions: { area: { marker: { enabled: !1, symbol: "circle", radius: 2, states: { hover: { enabled: !1 } } } }, lineWidth: 1, shadow: !1 },
        tooltip: { enabled: !1 },
        xAxis: { labels: { enabled: !1 }, title: { text: null }, startOnTick: !1, endOnTick: !1, tickPositions: [] },
        yAxis: { endOnTick: !1, startOnTick: !1, labels: { enabled: !1 }, title: { text: null }, tickPositions: [0] },
        credits: { enabled: !1 },
        series: [{ name: "", data: [] }],
    });
    e.yAxis[0].setExtremes(c, d), e.series[0].setData(b);
}
function initIndices(a, b) {
    function o(a, b) {
        return (
            a === b ||
            (!!a.children &&
                a.children.some(function (a) {
                    return o(a, b);
                }))
        );
    }
    function p(a) {
        if (a.children) {
            var b = a.children.map(p),
                c = d3.hsl(b[0]),
                d = d3.hsl(b[1]);
            return d3.hsl((c.h + d.h) / 2, 1.2 * c.s, c.l / 1.2);
        }
        return a.colour || "#fff";
    }
    function q(a) {
        var b = r(a),
            c = d3.interpolate(f.domain(), [a.x, a.x + a.dx]),
            d = d3.interpolate(g.domain(), [a.y, b]),
            h = d3.interpolate(g.range(), [a.y ? 20 : 0, e]);
        return function (a) {
            return function (b) {
                return f.domain(c(b)), g.domain(d(b)).range(h(b)), n(a);
            };
        };
    }
    function r(a) {
        return a.children ? Math.max.apply(Math, a.children.map(r)) : a.y + a.dy;
    }
    function s(a) {
        return 0.299 * a.r + 0.587 * a.g + 0.114 * a.b;
    }
    var c = a,
        d = c,
        e = c / 2,
        f = d3.scale.linear().range([0, 2 * Math.PI]),
        g = d3.scale.pow().exponent(1.3).domain([0, 1]).range([0, e]),
        h = 5,
        i = 1e3,
        k = d3.select("#vis");
    k.select("img").remove();
    var l = k
        .append("svg")
        .attr("width", c + 2 * h)
        .attr("height", d + 2 * h)
        .append("g")
        .attr("transform", "translate(" + [e + h, e + h] + ")"),
        m = d3.layout
            .partition()
            .sort(null)
            .value(function (a) {
                return 5.8 - a.depth;
            }),
        n = d3.svg
            .arc()
            .startAngle(function (a) {
                return Math.max(0, Math.min(2 * Math.PI, f(a.x)));
            })
            .endAngle(function (a) {
                return Math.max(0, Math.min(2 * Math.PI, f(a.x + a.dx)));
            })
            .innerRadius(function (a) {
                return Math.max(0, a.y ? g(a.y) : a.y);
            })
            .outerRadius(function (a) {
                return Math.max(0, g(a.y + a.dy));
            });
    d3.json(b, function (a, b) {
        function k(a) {
            a.children
                ? (d.transition().duration(i).attrTween("d", q(a)),
                    e
                        .style("visibility", function (b) {
                            return o(a, b) ? null : d3.select(this).style("visibility");
                        })
                        .transition()
                        .duration(i)
                        .attrTween("text-anchor", function (a) {
                            return function () {
                                return f(a.x + a.dx / 2) > Math.PI ? "end" : "start";
                            };
                        })
                        .attrTween("transform", function (a) {
                            var b = (a.name || "").split(" ").length > 1;
                            return function () {
                                var c = (180 * f(a.x + a.dx / 2)) / Math.PI - 90;
                                return "rotate(" + (c + (b ? -0.5 : 0)) + ")translate(" + (g(a.y) + h) + ")rotate(" + (c > 90 ? -180 : 0) + ")";
                            };
                        })
                        .style("fill-opacity", function (b) {
                            return o(a, b) ? 1 : 1e-6;
                        })
                        .each("end", function (b) {
                            d3.select(this).style("visibility", o(a, b) ? null : "hidden");
                        }))
                : (window.location.href = a.url);
        }
        var c = m.nodes({ children: b }),
            d = l.selectAll("path").data(c);
        d.enter()
            .append("path")
            .attr("id", function (a, b) {
                return "path-" + b;
            })
            .attr("d", n)
            .attr("fill-rule", "evenodd")
            .style("fill", p)
            .on("click", k);
        var e = l.selectAll("text").data(c),
            j = e
                .enter()
                .append("text")
                .style("fill-opacity", 1)
                .style("fill", function (a) {
                    return s(d3.rgb(p(a))) < 125 ? "#eee" : "#000";
                })
                .attr("text-anchor", function (a) {
                    return f(a.x + a.dx / 2) > Math.PI ? "end" : "start";
                })
                .attr("dy", ".2em")
                .attr("transform", function (a) {
                    var b = (a.name || "").split(" ").length > 1,
                        c = (180 * f(a.x + a.dx / 2)) / Math.PI - 90;
                    return "rotate(" + (c + (b ? -0.5 : 0)) + ")translate(" + (g(a.y) + h) + ")rotate(" + (c > 90 ? -180 : 0) + ")";
                })
                .on("click", k);
        j
            .append("tspan")
            .attr("x", 0)
            .text(function (a) {
                return a.depth ? a.name.split(" ")[0] : "";
            }),
            j
                .append("tspan")
                .attr("x", 0)
                .attr("dy", "1em")
                .text(function (a) {
                    return a.depth ? a.name.split(" ")[1] || "" : "";
                }),
            $("#path-0").css("fill", "#FFFFFF");
    });
}




function indicesSmall() {
    $(document).on("click", " .indicesBtn", function (a) {
        a.preventDefault(), $(".chart svg").remove();
        var b = $(this).attr("href");
        initIndices($(window).width() - 30, b), $(".indicesBtn").removeClass("active"), $(this).addClass("active");
    });
}
function getTickerData() {
    $(".indices_ticker .row").css("overflow", "hidden"),
        $.ajax({
            type: "GET",
            url: "https://liveindexsa.niftyindices.com/jsonfiles/TickerLiveIndicesWatch.json",
            data: { get_param: "data" },
            cache: !1,
            dataType: "json",
            success: function (a) {
                var b = 70;
                for (i = 0; i < a.length; i++) {
                    var c = a[i][0].last.replace(",", "") - a[i][0].previousClose.replace(",", "");
                    c = parseFloat(Math.round(100 * c) / 100).toFixed(2);
                    var d = "";
                    (d += '<div class="indicesScrolldiv">'),
                        (d += '<div class="pname">'),
                        //(d += '<img src="https://liveindexsa.niftyindices.com/assets/images/nifty.png">'),
                    // (d += "<span> " + a[i][0].indexName.slice(5) + "</span></div>"),
                        (d += "<span> " + a[i][0].indexName + "</span></div>"),
                        (d += '<ul class="list-inline">'),
                        (d += '<li class="pvalue">' + a[i][0].last + "</li>"),
                        c > 0
                            ? ((d += '<li class="greenvalue">' + c + "</li>"), (d += '<li class="greenpercentage">' + a[i][0].percChange + "%</li>"))
                            : ((d += '<li class="redvalue">' + c + "</li>"), (d += '<li class="redpercentage">' + a[i][0].percChange + "%</li>")),
                        (d += "</ul>"),
                        (d += "</div>"),
                        $(".indices_ticker .tickerContainer").append(d),
                        (b += Number($(".indices_ticker .indicesScrolldiv").outerWidth(!0) + 15));
                }
                $(".indices_ticker .tickerContainer").width(b), startTicker(b);
            },
            complete: function (a) { },
            error: function (a) { },
        });
}
function startTicker(a) {
    (timeline = new TimelineMax()), timeline.fromTo($(".indices_ticker .tickerContainer"), 170, { css: { marginLeft: $(".indices_ticker .row").width() } }, { css: { marginLeft: -a }, ease: Linear.easeNone, repeat: -1 });
}


// Jan07, 2026
function formatAsOn(input_) {
  var d = new Date(input_);
    var time = d.toLocaleTimeString().toUpperCase();
    var option2 = { day: 'numeric', month: 'long', year: 'numeric' };
    var newdate = d.toLocaleString('en-US', option2);   
        $('#advChartdate').html(newdate);
        $('#advCharttime').html(time);   
}

function stockindexwatchfile(a) {

    if (a == "NIFTY TATA 25 CAP") {
        a = "NIFTY INDIA CORPORATE GROUP INDEX - TATA GROUP 25 CAP";
    }

    var c = null,
        d = null;
    $.ajax({
        type: "GET",
        url: "https://liveindexsa.niftyindices.com/jsonfiles/LiveIndicesWatch.json",
        data: { get_param: "data" },
        cache: !1,
        dataType: "json",
        success: function (b) {
            if (b != null) {
                for (i = 0; i < b.data.length; i++)
                    if ((b.data[i].indexName.toLowerCase() == a.toLowerCase()) || (b.data[i].indexName.toLowerCase() == selval.toLowerCase()) || (b.data[i].indexName.toLowerCase() == strloc_mapname.toLowerCase())) {
                        $("#indexvalue").html(b.data[i].last),
                        formatAsOn(b.data[i].timeVal),
                            (c = b.data[i].last),
                            (c = c.replace(/\,/g, "")),
                            (c = parseFloat(c)),
                            (d = b.data[i].previousClose),
                            (d = d.replace(/\,/g, "")),
                            (d = parseFloat(d)),
                            (greenpercentage1 = c - d),
                            b.data[i].percChange > 0
                                ? ($("#indexgreenpercentage").removeClass("redpercentage"), $("#indexgreenpercentage").addClass("greenpercentage"))
                                : ($("#indexgreenpercentage").removeClass("greenpercentage"), $("#indexgreenpercentage").addClass("redpercentage")),
                            greenpercentage1 > 0
                                ? ($("#indexgreenvalue").removeClass("redvalue"), $("#indexgreenvalue").addClass("greenvalue"))
                                : ($("#indexgreenvalue").removeClass("greenvalue"), $("#indexgreenvalue").addClass("redvalue")),
                            "-" != b.data[i].percChange
                                ? $("#indexgreenvalue").html(b.data[i].percChange + "%")
                                : ($("#indexgreenvalue").html(""), $("#indexgreenvalue").removeClass("greenvalue"), $("#indexgreenvalue").removeClass("redvalue")),
                            isNaN(greenpercentage1)
                                ? ($("#indexgreenpercentage").html(""), $("#indexgreenpercentage").removeClass("redpercentage"), $("#indexgreenpercentage").removeClass("greenpercentage"))
                                : $("#indexgreenpercentage").html(greenpercentage1.toFixed(2));
                        break;
                    }
                -1 !== window.location.pathname.indexOf("index-movers") && ((strdate = b.data[0].timeVal), refreshDate(strdate));
            }
        },
        error: function (a) { },
    });
}
function IndexMapping(sname) {
    selval = "";
    strloc_mapname = "";
    var Iname = sname;

    if (Iname.toUpperCase() == "Nifty India Corporate Group Index - Tata Group 25 Cap".toUpperCase()) {
        Iname = "NIFTY INDIA CORPORATE GROUP INDEX - TATA GROUP 25% CAP";
    }

    data = "";
    $.ajax({
        type: "GET",
        url: "https://liveindexsa.niftyindices.com/assets/json/IndexMapping.json",
        data: "{}",
        async: !1,
        cache: !1,
        dataType: "json",
        success: function (data) {
            if (data != null) {
                Iname = Iname.toUpperCase().replace(/\s+/g, "");
                for (i = 0; i < data.length; i++) {
                    var mapval = data[i].Index_long_name.toUpperCase().replace(/\s+/g, "");
                    var trdval = data[i].Trading_Index_Name.toUpperCase().replace(/\s+/g, "");
                    if (mapval == Iname || trdval == Iname) {
                        selval = data[i].Trading_Index_Name;
                        strloc_mapname = data[i].Index_long_name;
                        break;
                    }
                }
            }
        },
    });
}
var counter = "";
function stockwatchfile(a, asynflag) {
    loadershow(), $(".btn-select-value").text(a);
    IndexMapping(a), (a = selval), (a = a.toUpperCase().trim());
    //if (a == 'NIFTY TOTAL MKT') {
    //    a = 'NIFTY 50';
    //}
    $.ajax({
        type: "GET",
        url: "https://liveindexsa.niftyindices.com/jsonfiles/equitystockwatch/EquityStockWatch" + a + ".json",
        data: "{}",
        async: asynflag,
        cache: !1,
        dataType: "json",
        success: function (a) {
            a.empty, (Sessionglobaldata = a), window.sessionStorage && sessionStorage.setItem("Sessionglobaldata", JSON.stringify(Sessionglobaldata)), (strdate = a.time), refreshDate(strdate);
            counter = a.data.length;
            //if (selval == "Nifty 500") {
            //    counter = 60;
            //    $("#loadmorestock").show();
            //}
            //else if (selval == "NIFTY TOTAL MKT" || selval == "NIFTY TOTAL MARKET" || selval == "Nifty Total MKT") {
            //    counter = 60;
            //    $("#loadmorestock").show();
            //}
            //else {
            //    counter = a.data.length;
            //    $("#loadmorestock").hide();
            //}
            //if (counter <= 55) {
            //    $("#loadmorestock").hide();
            //    counter = counter;
            //}
            //else {
            //    counter = 60;
            //    $("#loadmorestock").show();

            //}
            $("#loadmorestock").hide();
            counter = counter;
            for (
                $("#stockwatchtable tbody tr").remove(),
                $("#mobilewatch").html(""),
                $("#indexvalue").html(a.latestData[0].ltp),
                $("#indexgreenpercentage").html(a.latestData[0].ch),
                $("#indexgreenvalue").html(a.latestData[0].per),
                generatID = 1,
                i = 0;
                i < counter;
                i++
            ) {
                (nifty50 = a.data[i].ltP),
                    (nifty50 = nifty50.replace(/\,/g, "")),
                    (nifty50 = parseFloat(nifty50)),
                    (nifty50close = a.data[i].previousClose),
                    (nifty50close = nifty50close.replace(/\,/g, "")),
                    (nifty50close = parseFloat(nifty50close)),
                    //(Change = nifty50 - nifty50close),
                    (Change = a.data[i].ptsC),
                    (Change = Change.replace(/\,/g, "")),
                    (Change = parseFloat(Change)),
                    (PerChange = (Change / nifty50close) * 100);
                var c = $(window).width();
                if (c > 991)
                    $("#stockwatchtable").append(
                        "<tr><td>" +
                        a.data[i].symbol +
                        "</td><td><span id='perchangedesk" +
                        i +
                        "' class='shareDown'>" +
                        a.data[i].per +
                        "%</span></td><td><span id='changedesk" +
                        i +
                        "' class='red'>" +
                        Change.toFixed(2) +
                        "</span></td><td>" +
                        a.data[i].low +
                        "<div class='rel' id='low" +
                        i +
                        "'></div></td><td>" +
                        a.data[i].ltP +
                        "</td><td>" +
                        a.data[i].high +
                        "</td><td>" +
                        a.data[i].previousClose +
                        "</td><td>" +
                        a.data[i].open +
                        "</td><td>" +
                        a.data[i].trdVolM +
                        "</td><td>" +
                        a.data[i].mVal +
                        "</td><td>" +
                        a.data[i].wklo +
                        "</td><td>" +
                        a.data[i].wkhi +
                        "</td> </tr>"
                    ),
                        doSlide(),
                        a.data[i].per > 0 ? ($("#perchangedesk" + i).removeClass("shareDown"), $("#perchangedesk" + i).addClass("shareUp")) : ($("#perchangedesk" + i).removeClass("shareUp"), $("#perchangedesk" + i).addClass("shareDown")),
                        Change > 0 ? ($("#changedesk" + i).removeClass("red"), $("#changedesk" + i).addClass("green")) : ($("#changedesk" + i).removeClass("green"), $("#changedesk" + i).addClass("red"));
                else {
                    var d = "";
                    (d += '<div class="fundBlock">'),
                        (d += '<ul class="fundBlockIn">'),
                        (d += "<li>"),
                        (d += "<span>" + a.data[i].symbol + "</span>"),
                        (d += "<label>Symbol</label></li>"),
                        //(d += "<li>"),
                        //(d += '<span class="smallchart" id="areacontainer' + generatID + '" style="height: 50px; width:80px; margin: 0 auto"></span>'),
                        //(d += "<label>Today</label>"),
                        //(d += "</li>"),
                        (d += "<li>"),
                        (d += '<span id="perchange' + i + '" class="shareUp">' + a.data[i].per + "%</span>"),
                        (d += "<label>%Chng</label></li>"),
                        (d += "</ul>"),
                        (d += '<ul id="rel2' + i + '" class="fundBlockIn stockBar">'),
                        (d += "<li><span>" + a.data[i].low + "</span><label>Day Low</label></li>"),
                        (d += '<li><span class="green">' + a.data[i].ltP + "</span>"),
                        (d += "<label>LTP</label></li>"),
                        (d += "<li><span>" + a.data[i].high + "</span>"),
                        (d += "<label>Day HIGH</label></li></ul>"),
                        (d += '<ul class="fundBlockIn">'),
                        (d += "<li><span>" + a.data[i].previousClose + "</span>"),
                        (d += "<label>Prev Close</label></li>"),
                        (d += "<li><span>" + a.data[i].open + "</span><label>Day Open</label> </li>"),
                        (d += "<li><span>" + Change.toFixed(2) + "</span><label>chng</label></li></ul>"),
                        (d += '<ul class="fundBlockIn">'),
                        (d += "<li><span>" + a.data[i].wklo + "</span><label>52w LOW</label></li>"),
                        (d += "<li><span>" + a.data[i].wkhi + "</span><label>52w High</label></li></ul>"),
                        (d += '<ul class="fundBlockIn">'),
                        (d += "<li><span>" + a.data[i].trdVolM + "</span>"),
                        (d += "<label>Vol (Lacs)</label></li>"),
                        (d += "<li><span>" + a.data[i].mVal + "</span><label>(Crores) Turnover</label></li></ul>"),
                        (d += "</div>"),
                        $("#mobilewatch").append(d);
                    doSlide_mob("rel2" + i),
                        a.data[i].per > 0 ? ($("#perchange" + i).removeClass("shareDown"), $("#perchange" + i).addClass("shareUp")) : ($("#perchange" + i).removeClass("shareUp"), $("#perchange" + i).addClass("shareDown"));
                }
                generatID += 1;
            }
            if (c > 991) {
                var h = $("#stockwatchtable tbody tr").length;
                if (minNews + 15 <= h) {
                    minNews = minNews + 15;
                    d = minNews - 14;
                    //minNews = c
                    //d=minNews
                } else {
                    d = minNews + 1;
                    minNews = h;
                }

                //for (h <= minNews && (minNews = h), i = 0; i <= minNews; i++) {
                //for (h <= h, i = 1; i <= h; i++) {
                //    debugger;
                //    var j = $("#stockwatchtable tbody tr:nth-child(" + i + ")"),
                //        k = j.find("td:nth-child(2)").attr("id"),
                //        l = j.find("td:nth-child(1)").html(),
                //        m = k;
                //    initCMintraday(m, l);
                //}
            }
            else {
                var c = $(".fundBlock").length;

            }
            loaderhide(), $("#stockwatchtable tbody tr").hide(), c > 991 ? loadmoretable() : loadmoremobile();
        },//if (((minNews = minNews + 6 <= c ? minNews + 5 : c), (d = minNews - 4), (a = minNews - 5)))
        //    for (i = d; i <= minNews; i++) {
        //        var j = $("#mobilewatch .fundBlock:nth-child(" + i + ")"),
        //            k = j.find("ul li:nth-child(2) span").attr("id"),
        //            l = j.find("ul li:nth-child(1) span").html(),
        //            m = k;
        //        initCMintraday(m, l);
        //    }
        complete: function (a) {
            loaderhide();
        },
        error: function (a) {
            loaderhide();
        },
    });
}

function loadmoretable() {
    loadershow();
    var a = 0,
        b = JSON.parse(sessionStorage.Sessionglobaldata);
    $("#stockwatchtable tbody tr").hide();
    var c = $("#stockwatchtable tbody tr").length,
        d = 1;
    (minNews = 15), c < minNews && (minNews = c);
    var e = window.location.pathname,
        f = "equity-stock-watch",
        g = "exchange-traded-funds",
        h = "live-index-watch";
    if (-1 !== e.indexOf(f)) {
        minNews = c;
        $("#stockwatchtable tbody tr:lt(" + minNews + ")").show();
        var a = $("#stockwatchtable th:first"),
            b = a.index(),
            c = a.closest("table"),
            d = c.find("tbody > tr:visible").get();
        return (
            $(".sortArrow").removeClass("asending"),
            //$(".sortArrow").removeClass("desending"),
            $(this).addClass("asending")
                ? ($(this).removeClass("desc"),
                    $(this).addClass("asending"),
                    $(this).removeClass("desending"),
                    d.sort(function (a, c) {
                        if ("table-row" == $(d).css("display")) {
                            var e = $(a).children("td").eq(b).text().toUpperCase(),
                                f = $(c).children("td").eq(b).text().toUpperCase();
                            return b <= 1 ? Ascending(e, f) : Ascendingnum(e, f);
                        }
                    }))
                : ($(this).addClass("desc"),
                    $(this).removeClass("asending"),
                    $(this).addClass("desending"),
                    d.sort(function (a, c) {
                        if ("table-row" == $(d).css("display")) {
                            var e = $(a).children("td").eq(b).text().toUpperCase(),
                                f = $(c).children("td").eq(b).text().toUpperCase();
                            return b <= 1 ? Descending(e, f) : Descendingnum(e, f);
                        }
                    })),
            $.each(d, function (a, b) {
                c.children("tbody").append(b);
            }),
            !1
        );
        //for (i = d; i <= minNews; i++) { var l = $("#stockwatchtable tbody tr:nth-child(" + i + ")"), m = l.find("td:nth-child(2)").attr("id"), j //= l.find("td:nth-child(1)").html(), k = m; initCMintraday(k, j)
    }
    if (-1 !== e.indexOf(h))
        for (i = d; i <= minNews; i++) {
            var l = $("#stockwatchtable tbody tr:nth-child(" + i + ")"),
                m = l.find("td:nth-child(2)").attr("id"),
                j = l.find("td:nth-child(1) a").html(),
                k = m;
            initintraday(k, j);
        }
    if (-1 !== e.indexOf(g))
        for (i = d; i <= minNews; i++) {
            var l = $("#stockwatchtable tbody tr:nth-child(" + i + ")"),
                m = l.find("td:nth-child(3)").attr("id"),
                j = l.find("td:nth-child(1)").html(),
                k = m;
            initCMintraday(k, j);
        }
    $("#stockwatchtable tbody tr:lt(" + minNews + ")").show(),
        $("#loadmore").click(function (b) {
            b.preventDefault(), loadershow();
            var c = $("#stockwatchtable tbody tr").length;
            if (minNews + 16 <= c) {
                minNews = minNews + 15;
                d = minNews - 14;
            } else {
                d = minNews + 1;
                minNews = c;
            }
            if (-1 !== e.indexOf(f))
                for (c <= minNews && (minNews = c), i = d; i <= minNews; i++) {
                    var j = $("#stockwatchtable tbody tr:nth-child(" + i + ")"),
                        k = j.find("td:nth-child(2)").attr("id"),
                        l = j.find("td:nth-child(1)").html(),
                        m = k;
                    initCMintraday(m, l);
                }
            if (-1 !== e.indexOf(h))
                for (c <= minNews && (minNews = c), i = d; i <= minNews; i++) {
                    var j = $("#stockwatchtable tbody tr:nth-child(" + i + ")"),
                        k = j.find("td:nth-child(2)").attr("id"),
                        l = j.find("td:nth-child(1) a").html(),
                        m = k;
                    initintraday(m, l);
                }
            if (-1 !== e.indexOf(g))
                for (c <= minNews && (minNews = c), i = d; i <= minNews; i++) {
                    var j = $("#stockwatchtable tbody tr:nth-child(" + i + ")"),
                        k = j.find("td:nth-child(3)").attr("id"),
                        l = j.find("td:nth-child(1)").html(),
                        m = k;
                    initCMintraday(m, l);
                }
            $("tr:lt(" + (minNews + 1) + ")").show(), minNews + 1 >= c ? $("#loadmore").hide() : $("#loadmore").show();
        }),
        minNews + 1 >= c ? $("#loadmore").hide() : $("#loadmore").show();
}
function loadmoretableGainers() {
    loadershow();
    var a = 0,
        b = JSON.parse(sessionStorage.Sessionglobaldata);
    $("#stockwatchtableGainers tbody tr").hide();
    var c = $("#stockwatchtableGainers tbody tr").length,
        d = 1;
    (minNews = 15), c < minNews && (minNews = c);
    minNews = c;
    $("#stockwatchtableGainers tbody tr:lt(" + minNews + ")").show();

    //for (i = d; i <= minNews; i++) {
    //    var l = $("#stockwatchtableGainers tbody tr:nth-child(" + i + ")"),
    //        m = l.find("td:nth-child(2)").attr("id"),
    //        j = l.find("td:nth-child(1)").html(),
    //        k = m;
    //    initCMintraday(k, j)
    //}

    $("#stockwatchtableGainers tbody tr:lt(" + minNews + ")").show(),
        $("#loadmoreGainers").click(function (b) {
            b.preventDefault(), loadershow();
            var c = $("#stockwatchtableGainers tbody tr").length;
            if (minNews + 16 <= c) {
                minNews = minNews + 15;
                d = minNews - 14;
            } else {
                d = minNews + 1;
                minNews = c;
            }

            for (c <= minNews && (minNews = c), i = d; i <= minNews; i++) {
                var j = $("#stockwatchtableGainers tbody tr:nth-child(" + i + ")"),
                    k = j.find("td:nth-child(2)").attr("id"),
                    l = j.find("td:nth-child(1)").html(),
                    m = k;
                initCMintraday(m, l);
            }
            $("tr:lt(" + (minNews + 1) + ")").show(), minNews + 1 >= c ? $("#loadmoreGainers").hide() : $("#loadmoreGainers").show();
        });
    minNews + 1 >= c ? $("#loadmoreGainers").hide() : $("#loadmoreGainers").show();
}
function loadmoretableLosers() {
    loadershow();
    var a = 0,
        b = JSON.parse(sessionStorage.Sessionglobaldata);
    $("#stockwatchtableLosers tbody tr").hide();
    var c = $("#stockwatchtableLosers tbody tr").length,
        d = 1;
    (minNews = 15), c < minNews && (minNews = c);
    var e = window.location.pathname,
        f = "top-gainers-losers";

    if (-1 !== e.indexOf(f)) {
        minNews = c;
        $("#stockwatchtableLosers tbody tr:lt(" + minNews + ")").show();
        var a = $("#stockwatchtableLosers th:nth-child(3)");
        (b = a.index()), (c = a.closest("table")), (d = c.find("tbody > tr").get());
        //return $(".sortArrow").removeClass("asending"),
        return (
            $(".sortArrow").removeClass("desending"),
            $(this).addClass("asending")
                ? ($(this).removeClass("desc"),
                    $(this).addClass("asending"),
                    $(this).removeClass("desending"),
                    d.sort(function (a, c) {
                        if ("table-row" == $(d).css("display")) {
                            var e = $(a).children("td").eq(b).text().toUpperCase(),
                                f = $(c).children("td").eq(b).text().toUpperCase();
                            return b <= 1 ? Ascending(e, f) : Ascendingnum(e, f);
                        }
                    }))
                : ($(this).addClass("desc"),
                    $(this).removeClass("asending"),
                    $(this).addClass("desending"),
                    d.sort(function (a, c) {
                        if ("table-row" == $(d).css("display")) {
                            var e = $(a).children("td").eq(b).text().toUpperCase(),
                                f = $(c).children("td").eq(b).text().toUpperCase();
                            return b <= 1 ? Descending(e, f) : Descendingnum(e, f);
                        }
                    })),
            $.each(d, function (a, b) {
                c.children("tbody").append(b);
            }),
            !1
        );
    }
    //for (i = d; i <= minNews; i++) {
    //    var l = $("#stockwatchtableGainers tbody tr:nth-child(" + i + ")"),
    //        m = l.find("td:nth-child(2)").attr("id"),
    //        j = l.find("td:nth-child(1)").html(),
    //        k = m;
    //    initCMintraday(k, j)
    //}

    //$("#stockwatchtableLosers tbody tr:lt(" + minNews + ")").show(), $("#loadmoreLosers").click(function (b) {
    //    b.preventDefault(), loadershow();
    //    var c = $("#stockwatchtableLosers tbody tr").length;
    //    if (minNews + 16 <= c) {
    //        minNews = minNews + 15;
    //        d = minNews - 14
    //    }
    //    else {
    //        d = minNews + 1
    //        minNews = c

    //    }

    //    for (c <= minNews && (minNews = c), i = d; i <= minNews; i++) {
    //        var j = $("#stockwatchtableLosers tbody tr:nth-child(" + i + ")"),
    //            k = j.find("td:nth-child(2)").attr("id"),
    //            l = j.find("td:nth-child(1)").html(),
    //            m = k;
    //        initCMintraday(m, l)
    //    }
    //    $("tr:lt(" + (minNews + 1) + ")").show(), minNews + 1 >= c ? $("#loadmoreLosers").hide() : $("#loadmoreLosers").show()
    //}); minNews + 1 >= c ? $("#loadmoreLosers").hide() : $("#loadmoreLosers").show()
}
function loadmoremobile() {
    loadershow();
    var a = 0;
    JSON.parse(sessionStorage.Sessionglobaldata);
    $(".fundBlock").hide();
    var c = $(".fundBlock").length,
        d = 1;
    minNews = 5;
    var e = window.location.pathname,
        f = "equity-stock-watch",
        g = "exchange-traded-funds",
        h = "live-index-watch";
    if (-1 !== e.indexOf(f))
        for (i = d; i <= minNews; i++) {
            var j = $("#mobilewatch .fundBlock:nth-child(" + i + ")"),
                k = j.find("ul li:nth-child(2) span").attr("id"),
                l = j.find("ul li:nth-child(1) span").html(),
                m = k;
            //initCMintraday(m, l);
        }
    if (-1 !== e.indexOf(h))
        for (i = d; i <= minNews; i++) {
            var j = $("#mobilewatch .fundBlock:nth-child(" + i + ")"),
                k = j.find("ul li:nth-child(2) a span").attr("id"),
                l = j.find("ul li:nth-child(1) span a").html(),
                m = k;
            initintraday(m, l);
        }
    if (-1 !== e.indexOf(g))
        for (i = d; i <= minNews; i++) {
            var j = $("#mobilewatch .fundBlock:nth-child(" + i + ")"),
                k = j.find("ul li:nth-child(2) span").attr("id"),
                l = j.find("ul li:nth-child(3) span").html(),
                m = k;
            initintraday(m, l);
        }
    $("#mobilewatch .fundBlock:lt(" + minNews + ")").show(),
        $("#loadmore").click(function (b) {
            loadershow(), b.preventDefault();
            var c = $(".fundBlock").length;
            if (((minNews = minNews + 6 <= c ? minNews + 5 : c), (d = minNews - 4), (a = minNews - 5), -1 !== e.indexOf(f)))
                for (i = d; i <= minNews; i++) {
                    var j = $("#mobilewatch .fundBlock:nth-child(" + i + ")"),
                        k = j.find("ul li:nth-child(2) span").attr("id"),
                        l = j.find("ul li:nth-child(1) span").html(),
                        m = k;
                    //initCMintraday(m, l);
                }
            if (-1 !== e.indexOf(h))
                for (i = d; i <= minNews; i++) {
                    var j = $("#mobilewatch .fundBlock:nth-child(" + i + ")"),
                        k = j.find("ul li:nth-child(2) a span").attr("id"),
                        l = j.find("ul li:nth-child(1) span a").html(),
                        m = k;
                    initintraday(m, l);
                }
            if (-1 !== e.indexOf(g))
                for (i = d; i <= minNews; i++) {
                    var j = $("#mobilewatch .fundBlock:nth-child(" + i + ")"),
                        k = j.find("ul li:nth-child(2) span").attr("id"),
                        l = j.find("ul li:nth-child(3) span").html(),
                        m = k;
                    initintraday(m, l);
                }
            $(".fundBlock:lt(" + minNews + ")").show(), minNews >= c ? $("#loadmore").hide() : $("#loadmore").show();
        }),
        minNews >= c ? $("#loadmore").hide() : $("#loadmore").show();
}
function loadmoremobileGainers() {
    $(".gainers").hide();
    var a = $(".gainers").length,
        b = 5;
    $(".gainers:lt(" + b + ")").show(),
        $(".LoadMore").click(function (c) {
            c.preventDefault(), (b = b + 6 <= a ? b + 5 : a), $(".gainers:lt(" + b + ")").show(), b >= a && $(".LoadMore").hide();
        }),
        b >= a && $(".LoadMore").hide();
}
function loadmoremobileLosers() {
    $(".losers").hide();
    var a = $(".losers").length,
        b = 5;
    $(".losers:lt(" + b + ")").show(),
        $(".LoadMore").click(function (c) {
            c.preventDefault(), (b = b + 6 <= a ? b + 5 : a), $(".losers:lt(" + b + ")").show(), b >= a && $(".LoadMore").hide();
        }),
        b >= a && $(".LoadMore").hide();
}
function refresh() {
    var a = new Date(),
        b = { hour: "numeric", minute: "numeric", hour12: !0 },
        c = { day: "numeric", month: "long", year: "numeric" },
        d = a.toLocaleString("en-US", b),
        e = a.toLocaleString("en-US", c);
    $("#stockwatchdate").html(e), $("#stockwatchtime").html(d);
}
function refreshDate(a) {
    var b = new Date(a),
        c = { hour: "numeric", minute: "numeric", second: "numeric", hour12: !0 },
        d = { day: "numeric", month: "long", year: "numeric" },
        e = b.toLocaleString("en-US", c),
        f = b.toLocaleString("en-US", d);
    $("#stockwatchdate").html(f), $("#stockwatchtime").html(e);
}
function stockwatchrefresh() {
    loadershow();
    var a = $(".btn-select-value").text();
    asynflag = !1;
    stockwatchfile($.trim(a), asynflag);
}
function etfwatchrefresh() {
    loadershow(), readETFFile();
}
function IndexMoversrefresh() {
    loadershow();
    var a = $("#selecteIndex").text();
    HeatmapDetail($.trim(a));
}
function stockwatchGainersrefresh() {
    loadershow(), stockwatchGainersLosersfile($(".btn-select-value").text());
}
function Indiceswatchrefresh() {
    loadershow(), (asynflag = !1), readLiveIndexFile($(".btn-select-value").text(), asynflag);
}
function stockwatchGainersLosersfile(a) {
    IndexMapping(a);
    selval = selval.toUpperCase().trim();
    $.ajax({
        type: "GET",
        url: "https://liveindexsa.niftyindices.com/jsonfiles/equitystockwatch/EquityStockWatch" + selval + ".json",
        data: "{}",
        async: !0,
        cache: !1,
        dataType: "json",
        success: function (a) {
            (Sessionglobaldata = a), window.sessionStorage && sessionStorage.setItem("Sessionglobaldata", JSON.stringify(Sessionglobaldata));
            for ($("#stockwatchtableGainers tbody tr").remove(), $("#mobilewatchGainers").html(""), $("#stockwatchtableLosers tbody tr").remove(), $("#mobileWatchLosers").html(""), i = 0; i < a.data.length; i++) {
                (nifty50 = a.data[i].ltP),
                    (nifty50 = nifty50.replace(/\,/g, "")),
                    (nifty50 = parseFloat(nifty50)),
                    (nifty50close = a.data[i].previousClose),
                    (nifty50close = nifty50close.replace(/\,/g, "")),
                    (nifty50close = parseFloat(nifty50close)),
                    //(Change = nifty50 - nifty50close),
                    (Change = a.data[i].ptsC),
                    (Change = Change.replace(/\,/g, "")),
                    (Change = parseFloat(Change)),
                    (PerChange = (Change / nifty50close) * 100);
                var c = $(window).width();
                if (a.data[i].per >= 0)
                    if (c > 991)
                        $("#stockwatchtableGainers tbody").append(
                            "<tr><td>" +
                            a.data[i].symbol +
                            "</td><td><span id='perchangedesk" +
                            i +
                            "' class='shareUp'>" +
                            a.data[i].per +
                            "%</span></td><td><span id='changedesk" +
                            i +
                            "' class='green'>" +
                            Change.toFixed(2) +
                            "</span></td><td>" +
                            a.data[i].low +
                            "<div class='rel' id='low" +
                            i +
                            "'></div></td><td>" +
                            a.data[i].ltP +
                            "</td><td>" +
                            a.data[i].high +
                            "</td><td>" +
                            a.data[i].previousClose +
                            "</td><td>" +
                            a.data[i].open +
                            "</td><td>" +
                            a.data[i].trdVolM +
                            "</td><td>" +
                            a.data[i].mVal +
                            "</td><td>" +
                            a.data[i].wklo +
                            "</td><td>" +
                            a.data[i].wkhi +
                            "</td> </tr>"
                        ),
                            doSlide();
                    else {
                        var d = "";
                        (d += '<div class="fundBlock gainers">'),
                            (d += '<ul class="fundBlockIn">'),
                            (d += "<li>"),
                            (d += "<span>" + a.data[i].symbol + "</span>"),
                            (d += "<label>Symbol</label></li>"),
                            //(d += "<li>"),
                            //(d += '<span class="smallchart" id="areacontainer' + i + '" style="height: 50px; width:80px; margin: 0 auto"></span>'),
                            //(d += "<label>Today</label>"),
                            //(d += "</li>"),
                            (d += "<li>"),
                            (d += '<span id="perchange' + i + '" class="shareUp">' + a.data[i].per + "%</span>"),
                            (d += "<label>%Chng</label></li>"),
                            (d += "</ul>"),
                            (d += '<ul id="rel2' + i + '" class="fundBlockIn stockBar">'),
                            (d += "<li><span>" + a.data[i].low + "</span><label>Day Low</label></li>"),
                            (d += '<li><span class="green">' + a.data[i].ltP + "</span>"),
                            (d += "<label>LTP</label></li>"),
                            (d += "<li><span>" + a.data[i].high + "</span>"),
                            (d += "<label>Day HIGH</label></li></ul>"),
                            (d += '<ul class="fundBlockIn">'),
                            (d += "<li><span>" + a.data[i].previousClose + "</span>"),
                            (d += "<label>Prev Close</label></li>"),
                            (d += "<li><span>" + a.data[i].open + "</span><label>Day Open</label> </li>"),
                            (d += "<li><span>" + Change.toFixed(2) + "</span><label>chng</label></li></ul>"),
                            (d += '<ul class="fundBlockIn">'),
                            (d += "<li><span>" + a.data[i].wklo + "</span><label>52w LOW</label></li>"),
                            (d += "<li><span>" + a.data[i].wkhi + "</span><label>52w High</label></li></ul>"),
                            (d += '<ul class="fundBlockIn">'),
                            (d += "<li><span>" + a.data[i].trdVolM + "</span>"),
                            (d += "<label>Vol (Lacs)</label></li>"),
                            (d += "<li><span>" + a.data[i].mVal + "</span><label>(Crores) Turnover</label></li></ul>"),
                            (d += "</div>"),
                            $("#mobilewatchGainers").append(d);
                        var e = "rel2" + i;
                        doSlide_mob(e);
                    }
                else if (c > 991)
                    $("#stockwatchtableLosers tbody").append(
                        "<tr><td>" +
                        a.data[i].symbol +
                        "</td><td><span class='shareDown'>" +
                        a.data[i].per +
                        "%</span></td><td><span class='red'>" +
                        Change.toFixed(2) +
                        "</span></td><td>" +
                        a.data[i].low +
                        "<div class='rel' id='low" +
                        i +
                        "'></div></td><td>" +
                        a.data[i].ltP +
                        "</td><td>" +
                        a.data[i].high +
                        "</td><td>" +
                        a.data[i].previousClose +
                        "</td><td>" +
                        a.data[i].open +
                        "</td><td>" +
                        a.data[i].trdVolM +
                        "</td><td>" +
                        a.data[i].mVal +
                        "</td><td>" +
                        a.data[i].wklo +
                        "</td><td>" +
                        a.data[i].wkhi +
                        "</td> </tr>"
                    ),
                        doSlide();
                else {
                    var d = "";
                    (d += '<div class="fundBlock losers">'),
                        (d += '<ul class="fundBlockIn">'),
                        (d += "<li>"),
                        (d += "<span>" + a.data[i].symbol + "</span>"),
                        (d += "<label>Symbol</label></li>"),
                        //(d += "<li>"),
                        //(d += '<span class="smallchart" id="areacontainer' + i + '" style="height: 50px; width:80px; margin: 0 auto"></span>'),
                        //(d += "<label>Today</label>"),
                        //(d += "</li>"),
                        (d += "<li>"),
                        (d += '<span class="shareDown">' + a.data[i].per + "%</span>"),
                        (d += "<label>%Chng</label></li>"),
                        (d += "</ul>"),
                        (d += '<ul id="rel2' + i + '" class="fundBlockIn stockBar">'),
                        (d += "<li><span>" + a.data[i].low + "</span><label>Day Low</label></li>"),
                        (d += '<li><span class="red">' + a.data[i].ltP + "</span>"),
                        (d += "<label>LTP</label></li>"),
                        (d += "<li><span>" + a.data[i].high + "</span>"),
                        (d += "<label>Day HIGH</label></li></ul>"),
                        (d += '<ul class="fundBlockIn">'),
                        (d += "<li><span>" + a.data[i].previousClose + "</span>"),
                        (d += "<label>Prev Close</label></li>"),
                        (d += "<li><span>" + a.data[i].open + "</span><label>Day Open</label> </li>"),
                        (d += "<li><span>" + Change.toFixed(2) + "</span><label>chng</label></li></ul>"),
                        (d += '<ul class="fundBlockIn">'),
                        (d += "<li><span>" + a.data[i].wklo + "</span><label>52w LOW</label></li>"),
                        (d += "<li><span>" + a.data[i].wkhi + "</span><label>52w High</label></li></ul>"),
                        (d += '<ul class="fundBlockIn">'),
                        (d += "<li><span>" + a.data[i].trdVolM + "</span>"),
                        (d += "<label>Vol (Lacs)</label></li>"),
                        (d += "<li><span>" + a.data[i].mVal + "</span><label>(Crores) Turnover</label></li></ul>"),
                        (d += "</div>"),
                        $("#mobilewatchGainers").append(d);
                    var e = "rel2" + i;
                    doSlide_mob(e);
                }
            }
            c > 991 ? (loadmoretableGainers(), loadmoretableLosers()) : (loadmoremobileGainers(), loadmoremobileLosers());
            (strdate = a.time), refreshDate(strdate), loaderhide();
        },
        error: function (a) {
            console.log(a);
        },
    });
}
function Ascendingnum(a, b) {
    return parseFloat(a) < parseFloat(b) ? -1 : parseFloat(a) > parseFloat(b) ? 1 : 0;
}
function Ascending(a, b) {
    return a < b ? -1 : a > b ? 1 : 0;
}
function Descendingnum(a, b) {
    return parseFloat(a) < parseFloat(b) ? 1 : parseFloat(a) > parseFloat(b) ? -1 : 0;
}
function Descending(a, b) {
    return a < b ? 1 : a > b ? -1 : 0;
}
function setPriceSlider(a, b, c, d) {
    (a = a), (b = b.replace(/\,/g, "")), (d = d.replace(/\,/g, "")), (c = c.replace(/\,/g, ""));
    var e = parseFloat(parseFloat(d).toFixed(2) - parseFloat(c).toFixed(2)).toFixed(2),
        f = parseFloat(parseFloat(b).toFixed(2) - parseFloat(c).toFixed(2)).toFixed(2),
        g = parseFloat((212 * parseFloat(f).toFixed(2)) / parseFloat(e)).toFixed(2);
    return (
        "#" +
        a +
        ':after { content: ""; position: absolute; top: 2px; left: ' +
        parseFloat(parseFloat(g) - 5).toFixed(2) +
        'px; background-image: url("https://liveindexsa.niftyindices.com/assets/images/ico-rel-arrow.png"); background-repeat: no-repeat; width: 10px; height: 6px;}'
    );
}
function setPriceSliderliveindexwatch(a, b, c, d) {
    (b = b.replace(/\,/g, "")), (d = d.replace(/\,/g, "")), (c = c.replace(/\,/g, ""));
    var f = (parseFloat(c), parseFloat(d), parseFloat(parseFloat(d).toFixed(2) - parseFloat(c).toFixed(2)).toFixed(2)),
        g = parseFloat(parseFloat(b).toFixed(2) - parseFloat(c).toFixed(2)).toFixed(2),
        h = parseFloat((265 * parseFloat(g).toFixed(2)) / parseFloat(f)).toFixed(2);
    return (
        "#" +
        a +
        ':after { content: ""; position: absolute; top: 2px; left: ' +
        parseFloat(parseFloat(h) - 5).toFixed(2) +
        'px; background-image: url("https://liveindexsa.niftyindices.com/assets/images/ico-rel-arrow.png"); background-repeat: no-repeat; width: 10px; height: 6px;}'
    );
}
function setPriceSliderETF(a, b, c, d) {
    (b = b.replace(/\,/g, "")), (d = d.replace(/\,/g, "")), (c = c.replace(/\,/g, ""));
    var f = (parseFloat(c), parseFloat(d), parseFloat(parseFloat(d).toFixed(2) - parseFloat(c).toFixed(2)).toFixed(2)),
        g = parseFloat(parseFloat(b).toFixed(2) - parseFloat(c).toFixed(2)).toFixed(2),
        h = parseFloat((265 * parseFloat(g).toFixed(2)) / parseFloat(f)).toFixed(2);
    return (
        "#" +
        a +
        ':after { content: ""; position: absolute; top: 2px; left: ' +
        parseFloat(parseFloat(h) - 5).toFixed(2) +
        'px; background-image: url("https://liveindexsa.niftyindices.com/assets/images/ico-rel-arrow.png"); background-repeat: no-repeat; width: 10px; height: 6px;}'
    );
}
function doSlide() {
    var a = "";
    $.each($("#stockwatchtable  tbody tr,#stockwatchtableGainers tbody tr,#stockwatchtableLosers tbody tr"), function (b, c) {
        var d = $(this).find("td:nth-child(4) .rel").attr("id"),
            e = $(this).find("td:nth-child(4)").text(),
            f = $(this).find("td:nth-child(5)").text(),
            g = $(this).find("td:nth-child(6)").text();
        a += setPriceSlider(d, f, e, g) + "\n";
    });
    var b = $('<style data-id="cont-1-css"> ' + a + "</style>");
    $("html > head").append(b), (id = null), (low = null), (high = null), (ltp = null);
}
function doSlide_mob(a) {
    $(".maToggle").hasClass("active") ||
        $.each($(".fundBlock"), function (b, c) {
            var d = a,
                e = $(this).find(".stockBar li:nth-child(1) span").text(),
                f = $(this).find(".stockBar li:nth-child(2) span").text(),
                g = $(this).find(".stockBar li:nth-child(3) span").text(),
                h = parseFloat(parseFloat(g).toFixed(2) - parseFloat(e).toFixed(2)).toFixed(2),
                i = parseFloat(parseFloat(f).toFixed(2) - parseFloat(e).toFixed(2)).toFixed(2),
                j = parseFloat((180 * parseFloat(i).toFixed(2)) / parseFloat(h)).toFixed(2),
                k = parseFloat(parseFloat(j) - 5).toFixed(2),
                l = $('<style data-id="cont-1-css"> .mobileWatch #' + d + ".stockBar:after { top: 2px; left:" + k + "px;}</style>");
            $("html > head").append(l);
        });
}
function doSildeLiveIndexwatch() {
    var a = "";
    $.each($("#stockwatchtable tbody tr"), function (b, c) {
        var d = $(this).find("td:nth-child(5) .rel").attr("id"),
            e = $(this).find("td:nth-child(5)").text(),
            f = $(this).find("td:nth-child(6)").text(),
            g = $(this).find("td:nth-child(7)").text();
        a += setPriceSliderliveindexwatch(d, f, e, g) + "\n";
    });
    var b = $('<style data-id="cont-1-css"> ' + a + "</style>");
    $("html > head").append(b);
}
function doSilderETF() {
    var a = "";
    $.each($("#stockwatchtable tbody tr"), function (b, c) {
        var d = $(this).find("td:nth-child(6) .rel").attr("id"),
            e = $(this).find("td:nth-child(6)").text(),
            f = $(this).find("td:nth-child(7)").text(),
            g = $(this).find("td:nth-child(8)").text();
        a += setPriceSliderETF(d, f, e, g) + "\n";
    });
    var b = $('<style data-id="cont-1-css"> ' + a + "</style>");
    $("html > head").append(b);
}
function doSilderETF_mob(a) {
    $(".maToggle").hasClass("active") ||
        $.each($(".fundBlock"), function (b, c) {
            var d = a,
                e = $(this).find(".stockBar li:nth-child(1) span").text(),
                f = $(this).find(".stockBar li:nth-child(2) span").text(),
                g = $(this).find(".stockBar li:nth-child(3) span").text(),
                h = (parseFloat(e) + parseFloat(g)) / 2,
                i = parseFloat(g) - parseFloat(h),
                j = parseFloat(f) - parseFloat(h),
                k = (parseFloat(j) / parseFloat(i)) * 100;
            if (parseFloat(k) < 0) {
                k = Math.abs(k);
                var l = parseFloat(115 + parseFloat(k)).toFixed(2);
            } else var l = parseFloat(115 - parseFloat(k)).toFixed(2);
            var m = parseFloat(parseFloat(l) - 5).toFixed(2);
            isNaN(l) && (j = -5);
            var n = $('<style data-id="cont-1-css"> .mobileWatch #' + d + ".stockBar:after { top: 2px; left:" + m + "px;}</style>");
            $("html > head").append(n);
        });
}
function doSildeLiveIndexwatch_mob(a) {
    $(".maToggle").hasClass("active") ||
        $.each($(".fundBlock"), function (b, c) {
            var d = a,
                e = $(this).find(".stockBar li:nth-child(1) span").text(),
                f = $(this).find(".stockBar li:nth-child(2) span").text(),
                g = $(this).find(".stockBar li:nth-child(3) span").text(),
                h = (parseFloat(e) + parseFloat(g)) / 2,
                i = parseFloat(g) - parseFloat(h),
                j = parseFloat(f) - parseFloat(h),
                k = (parseFloat(j) / parseFloat(i)) * 100;
            if (parseFloat(k) < 0) {
                k = Math.abs(k);
                var l = parseFloat(115 + parseFloat(k)).toFixed(2);
            } else var l = parseFloat(115 - parseFloat(k)).toFixed(2);
            var m = parseFloat(parseFloat(l) - 5).toFixed(2);
            isNaN(l) && (j = -5);
            var n = $('<style data-id="cont-1-css"> .mobileWatch #' + d + ".stockBar:after { top: 2px; left:" + m + "px;}</style>");
            $("html > head").append(n);
        });
}
function HistoricalDataFile() {
    $(".noData").hide(), $(".historyData-show").fadeIn();
    var a = $("#ddlHistorical").val();
    $.ajax({
        type: "GET",
        url: "https://liveindexsa.niftyindices.com/assets/json/HistoricalData.json",
        data: "{}",
        async: !1,
        cache: !1,
        dataType: "json",
        success: function (b) {
            if (0 == b.length) HistoricalData(a);
            else
                for (i = 0; i < b.length; i++) {
                    var d = $(window).width();
                    d > 991 && $("#history tbody").append("<tr><td>" + b[i].date + "</td><td>" + b[i].open + "</td><td>" + b[i].high + "</td><td>" + b[i].low + "</td><td>" + b[i].close + "</td></tr>");
                }
        },
        error: function (a) { },
    });
}
function HistoricalData(indexname, Datestart, dateEnd) {
    if (indexname == "" || indexname == null || indexname == "0") {
        return window.alert("Please select valid Index name.")
    }

    /*Start 28-08-2025: Date cannot be selected more than 1 year*/
    let start = new Date(Datestart);
    let end = new Date(dateEnd);
    let timeDifference = end - start;
    const diffDays = Math.ceil(timeDifference / (1000 * 60 * 60 * 24));
    if (diffDays > 365) {
        return window.alert("Please select date range not more than 1 Year");
    }
    else if (diffDays < 0) {
        return window.alert("Start date can not be greater than End Date");
    }
    /*End 28-08-2025: Date cannot be selected more than 1 year*/

    var tableIndexNameH; // May21,2024
    loadershow();
    $("#nodatafound").hide(), $("#history").hide();
    $("#HistoryExport").hide();
    var current_page = 1,
        startDate = Datestart,
        endDate = dateEnd;
    IndexMapping(indexname),
        name = selval,
        // For Local use the below, otherwise use the above
        //name = indexname,
        name = name.toUpperCase().trim();
    //var jsonData = "{'name':'" + name + "','startDate':'" + startDate + "','endDate':'" + endDate + "'}";
    var jsonData = "{'name':'" + name + "','startDate':'" + startDate + "','endDate':'" + endDate + "','indexName':'" + indexname + "'}";
    var sendjson = {};
    sendjson.cinfo = jsonData;
    //var jsonData = "{'name':'" + name + "','startDate':'" + startDate + "','endDate':'" + endDate + "'}";
    return $.ajax({
        type: "POST",
        data: JSON.stringify(sendjson),
        //data: "{'name':'" + name + "','startDate':'" + startDate + "','endDate':'" + endDate + "'}",
        url: "/BackPage/getHistoricaldatatabletoString",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        async: !0,
        success: function (result) {

            $("#exportArchives").hide();



            if (result != null && result != 0) {
                //var htmldata = "string" == typeof result ? eval("(" + result + ")") : result;

                var htmldata = typeof result === "string" ? JSON.parse(result.d) : result;
                console.log(result);


                trHtml += '<table><thead><tr><th>DATE</th><th>OPEN</th><th>HIGH</th><th>LOW</th><th>CLOSE</th></tr></thead>';
                trHtml += '<tbody>';
                $("#HistoryExport tbody").html("");
                // Nov21,2023 to replace endash('–') with hyphen('-') just only in exportFile
                var Properindexname = indexname.replace(/\u2013/g, "-");
                for (var b = 0; b < htmldata.length; b++) {
                    tableIndexNameH = htmldata[b].INDEX_NAME.toUpperCase(); // May21,2024
                    //trHtml += '<tr><td>' + htmldata[f].HistoricalDate + '</td><td>' + htmldata[f].OPEN + '</td><td>' + htmldata[f].HIGH + '</td><td>' + htmldata[f].LOW + '</td><td>' + htmldata[f].CLOSE + '</td></tr>';
                    $("#HistoryExport tbody").append("<tr><td>" + Properindexname + "</td><td>" + htmldata[b].HistoricalDate + "</td><td>" + htmldata[b].OPEN + "</td><td>" + htmldata[b].HIGH + "</td><td>" + htmldata[b].LOW + "</td><td>" + htmldata[b].CLOSE + "</td></tr>");

                }
                if (tableIndexNameH == indexname || tableIndexNameH == name) {
                    tableIndexNameH = indexname
                }
                trHtml += '</tbody>';
                trHtml += '</table>';

                $("#history tbody tr").remove(), $("#mobiledata").html("");
                function changePage(a) {
                    a < 1 && (a = 1), a > numPages() && (a = numPages()), $("#history tbody tr").remove(),
                        $("#mobiledata").html("");

                    for (var b = (a - 1) * elements_per_page; b < a * elements_per_page && b < p.length; b++) {
                        if ($(window).width() > 991)
                            $("#Indexname").html(tableIndexNameH), //updated May21,2024
                                $("#datenotehistorical").show(),
                                $("#history tbody").append("<tr><td>" + p[b].HistoricalDate + "</td><td>" + p[b].OPEN + "</td><td>" + p[b].HIGH + "</td><td>" + p[b].LOW + "</td><td>" + p[b].CLOSE + "</td></tr>");

                        else {
                            $("#Indexname").html(tableIndexNameH); //updated May21,2024
                            $("#datenotehistorical").show();
                            var d = "";

                            d += '<div class="fundBlock">', d += '<ul class="fundBlockIn">', d += "<li>", d += "<span>" + p[b].HistoricalDate + "</span>", d += "<label>date</label></li>", d += "<li>", d += "<span>" + p[b].HIGH + "</span>", d += "<label>day high</label></li>", d += "</ul>", d += '<ul  class="fundBlockIn">', d += "<li><span>" + p[b].OPEN + "</span><label>open</label></li>", d += "<li><span>" + p[b].LOW + "</span>", d += "<label>Day low</label></li>", d += "<li><span>" + p[b].CLOSE + "</span>", d += "<label>Day close</label></li></ul>", d += "</div>", $("#mobiledata").append(d), $("#mobiledata").fadeIn()
                        }
                    }
                    btn_prev.style.visibility = 1 == a ? "hidden" : "visible", a == numPages() ? btn_next.style.visibility = "hidden" : btn_next.style.visibility = "visible"
                }

                function numPages() {
                    return Math.ceil(max_size / elements_per_page)
                }

                function prevPage() {
                    current_page > 1 && (current_page--, changePage(current_page))
                }

                function nextPage() {
                    current_page < numPages() && (current_page++, changePage(current_page))
                }

                //if ($("#history tbody tr").remove(), $("#mobiledata").html(""), "[]" == result.d) $("#nodatafound").show(), $(".downloads").hide(), $("#pagehistoricaldata").hide(), $("#Historicalnodata").hide(), $(".historyData-show").hide();
                if ($("#history tbody tr").remove(), $("#mobiledata").html(""), "[]" == result)window.alert("Please check the date range and try again."), $("#nodatafound").show(), $(".downloads").hide(), $("#pagehistoricaldata").hide(), $("#Historicalnodata").hide(), $(".historyData-show").hide();
                else {
                    $("#nodatafound").hide(), $("#Historicalnodata").hide(), $(".historyData-show").show(), $("#history").show(), $(".downloads").show(), $("#pagehistoricaldata").show(), $("#Indexname").show(), $("#exporthistorical").show();
                    var p = "string" == typeof result ? eval("(" + result.d + ")") : result,
                        max_size = p.length,
                        sta = 0,
                        elements_per_page = 300,
                        limit = elements_per_page,
                        btn_next = document.getElementById("btn_next"),
                        btn_prev = document.getElementById("btn_prev");
                    changePage(current_page), $("#btn_next").click(function () {
                        nextPage()
                    }), $("#btn_prev").click(function () {
                        prevPage()
                    })
                }

            }
            else {
                window.alert("Please check the date range and try again.");
                $("#Historicalnodata").hide();

                $("#nodatafound").show();
            }

        },

        complete: function (a) {
            loaderhide();
        },
        error: function (a, b, c) {
            JSON.parse(a.responseText)
        }
    }), !1
    // loaderhide();

}
function HistoricalIndiavixData(indexname, Datestart, dateEnd) {
    $(".noData").hide();
    var name = indexname,
        startDate = Datestart,
        endDate = dateEnd;
    return (
        $.ajax({
            type: "POST",
            data: "{'name':'" + name + "','startDate':'" + startDate + "','endDate':'" + endDate + "'}",
            url: "/BackPage/BindHistoricalIndiaVixData",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            async: !0,
            success: function (result) {
                if (($("#historyvixdata tbody tr").remove(), $("#mobilevix").html(""), "false" == result.d.toLowerCase())) $(".downloads").hide(), $("#pagehistoricalvixdata").hide();
                else {
                    $(".downloads").show(), $("#pagehistoricalvixdata").show();
                    for (var p = "string" == typeof result.d ? eval("(" + result.d + ")") : result.d, i = 0; i < p.length; i++) {
                        var widthsize = $(window).width();
                        if (widthsize > 991)
                            $("#IndiaVixname").html(name),
                                $("#historyvixdata tbody").append(
                                    "<tr><td>" +
                                    p[i].date +
                                    "</td><td>" +
                                    p[i].open +
                                    "</td><td>" +
                                    p[i].high +
                                    "</td><td>" +
                                    p[i].low +
                                    "</td><td>" +
                                    p[i].close +
                                    "</td><td>" +
                                    p[i].close +
                                    "</td><td>" +
                                    p[i].close +
                                    "</td><td>" +
                                    p[i].close +
                                    "</td></tr>"
                                );
                        else {
                            var table = "";
                            (table += '<div class="fundBlock">'),
                                (table += '<ul class="fundBlockIn">'),
                                (table += "<li>"),
                                (table += "<span>" + p[i].date + "</span>"),
                                (table += "<label>date</label></li>"),
                                (table += "<li>"),
                                (table += "<span>" + p[i].high + "</span>"),
                                (table += "<label>day high</label></li>"),
                                (table += "</ul>"),
                                (table += '<ul  class="fundBlockIn">'),
                                (table += "<li><span>" + p[i].open + "</span><label>open</label></li>"),
                                (table += "<li><span>" + p[i].low + "</span>"),
                                (table += "<label>Day low</label></li>"),
                                (table += "<li><span>" + p[i].close + "</span>"),
                                (table += "<label>Day close</label></li>"),
                                (table += "<li><span>" + p[i].close + "</span>"),
                                (table += "<label>Prev Close</label></li>"),
                                (table += "<li><span>" + p[i].close + "</span>"),
                                (table += "<label>Change</label></li>"),
                                (table += "<li><span>" + p[i].close + "</span>"),
                                (table += "<label>% Change</label></li></ul>"),
                                (table += "</div>"),
                                $("#mobilevix").append(table),
                                $("#mobilevix").fadeIn();
                        }
                    }
                }
            },
            error: function (a, b, c) {
                JSON.parse(a.responseText);
            },
        }),
        !1
    );
}


function Historicaldivyield(indexname, Datestart, dateEnd) {
    if (indexname == "" || indexname == null || indexname == "0") {


        // Hide the element
        $("#historytotalindex").hide();
        document.getElementById("historytotalindex").style.display = "none";


        // Remove any class that might be forcing visibility
        $("#historytotalindex").removeClass("historyData-show show");


        // Force hide after a small delay in case another script is overriding it
        setTimeout(function () {
            $("#historytotalindex").hide();
            document.getElementById("historytotalindex").style.display = "none";
            document.getElementById("TotalReturnnodatafound").style.display = "none";

        }, 100);

        $("#TotalReturnnodatafound").hide();
        alert("Please select a valid Index name.");

        //    return window.alert("Please select valid Index name.")
    }

    /*Start 28-08-2025: Date cannot be selected more than 1 year*/
    let start = new Date(Datestart);
    let end = new Date(dateEnd);
    let timeDifference = end - start;
    const diffDays = Math.ceil(timeDifference / (1000 * 60 * 60 * 24));
    if (diffDays > 365) {
        return window.alert("Please select date range not more than 1 Year");
    }
    else if (diffDays < 0) {
        return window.alert("Start date can not be greater than End Date");
    }
    /*End 28-08-2025: Date cannot be selected more than 1 year*/
    var tableIndexNameP;
    loadershow();
    $("#historydivyieldexport").hide();
    $("#noDivdatafound").hide(), $("#historydivyield").hide();
    var current_page = 1,
        startDate = Datestart,
        endDate = dateEnd;
    IndexMapping(indexname),
        name = selval,
        name = name.toUpperCase().trim();
    var jsonData = "{'name':'" + name + "','startDate':'" + startDate + "','endDate':'" + endDate + "','indexName':'" + indexname + "'}";
    var sendjson = {};
    sendjson.cinfo = jsonData;

    return $.ajax({
        type: "POST",
        //data: "{'name':'" + name + "','startDate':'" + startDate + "','endDate':'" + endDate + "'}",
        data: JSON.stringify(sendjson),
        url: "/BackPage/getpepbHistoricaldataDBtoString",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        async: !0,
        success: function (result) {
            if (result != null && result != 0) {
                //var htmldata = "string" == typeof result.d ? eval("(" + result.d + ")") : result.d;

                var htmldata = typeof result === "string" ? JSON.parse(result.d) : result;


                //trHtml += '<table><thead><tr><th>DATE</th><th>OPEN</th><th>HIGH</th><th>LOW</th><th>CLOSE</th></tr></thead>';
                //trHtml += '<tbody>';
                $("#historydivyieldexport tbody").html("");
                // Nov21,2023 to replace endash('–') with hyphen('-') just only in exportFile
                var Properindexname = indexname.replace(/\u2013/g, "-");
                for (var b = 0; b < htmldata.length; b++) {
                    tableIndexNameP = htmldata[b]["Index Name"].toUpperCase();
                    //trHtml += '<tr><td>' + htmldata[f].HistoricalDate + '</td><td>' + htmldata[f].OPEN + '</td><td>' + htmldata[f].HIGH + '</td><td>' + htmldata[f].LOW + '</td><td>' + htmldata[f].CLOSE + '</td></tr>';
                    //$("#historydivyieldexport tbody").append("<tr><td class='thIndexName'>" + htmldata[b]["Index Name"].toUpperCase() + "</td><td class='thdate'>" + htmldata[b].DATE + "</td><td class='thpe'>" + htmldata[b].pe + "</td><td class='thpb'>" + htmldata[b].pb + "</td><td class='thdiv'>" + htmldata[b].divYield + "</td></tr>");
                    $("#historydivyieldexport tbody").append("<tr><td class='thIndexName'>" + Properindexname + "</td><td class='thdate'>" + htmldata[b].DATE + "</td><td class='thpe'>" + htmldata[b].pe + "</td><td class='thpb'>" + htmldata[b].pb + "</td><td class='thdiv'>" + htmldata[b].divYield + "</td></tr>");
                }
                if (tableIndexNameP == indexname || tableIndexNameP == name) {
                    tableIndexNameP = indexname
                }
                $("#historydivyield tbody tr").remove(), $("#mobilediv").html("");
                function changePage(a) {
                    a < 1 && (a = 1), a > numPages() && (a = numPages()), $("#historydivyield tbody tr").remove(), $("#mobilediv").html("");
                    for (var b = (a - 1) * elements_per_page; b < a * elements_per_page && b < p.length; b++) {
                        if ($(window).width() > 991) $("#Indexdivname").html(tableIndexNameP), //updated May21,2024
                            $("#datenotehistoricalpepb").show(),
                            $("#historydivyield tbody").append("<tr><td class='thdate'>" + p[b].DATE + "</td><td class='thpe'>" + p[b].pe + "</td><td class='thpb'>" + p[b].pb + "</td><td class='thdiv'>" + p[b].divYield + "</td></tr>");
                        else {
                            $("#Indexdivname").html(tableIndexNameP); //updated May21,2024
                            $("#datenotehistoricalpepb").show();
                            var d = "";
                            d += '<div class="fundBlock">', d += '<ul class="fundBlockIn">', d += '<li class="thdate">', d += "<span >" + p[b].DATE + "</span>",
                                d += "<label>date</label></li>",
                                d += '<li class="thpe">',
                                d += "<span >" + p[b].pe + "</span>",
                                d += "<label>pe</label></li>",
                                d += "</ul>", d += '<ul  class="fundBlockIn">',
                                d += '<li class="thpb"><span>' + p[b].pb + "</span>",
                                d += "<label>pb</label></li>",
                                d += '<li class="thdiv"><span >' + p[b].divYield + "</span><label>divYield %</label></li></ul>",
                                d += "</div>", $("#mobilediv").append(d), $("#mobilediv").fadeIn()
                        }
                    }
                    $("#pe").is(":checked", !0) || $(".thpe").hide(), $("#pb").is(":checked", !0) || $(".thpb").hide(), $("#yield").is(":checked", !0) || $(".thdiv").hide(), $("#all").is(":checked", !0) && ($(".thpe").show(), $(".thdiv").show(), $(".thpb").show()), btn_prev.style.visibility = 1 == a ? "hidden" : "visible", a == numPages() ? btn_next.style.visibility = "hidden" : btn_next.style.visibility = "visible"
                }

                function numPages() {
                    return Math.ceil(max_size / elements_per_page)
                }

                function prevPage() {
                    current_page > 1 && (current_page--, changePage(current_page))
                }

                function nextPage() {
                    current_page < numPages() && (current_page++, changePage(current_page))
                }
                if ($("#historydivyield tbody tr").remove(), $("#mobilediv").html(""), "[]" == result) $("#noDivdatafound").show(), $(".downloads").hide(), $(".historyData-show").hide(), $("#pagehistoricalpepbdata").hide(), $("#historydivyield").hide();
                else { // Below line updated on Jul09-2024
                    $(".noData text-center").hide(), $(".historyData-show").show(), $("#historydivyield").show(), $(".downloads,.pull_right").show(), $("#pagehistoricalpepbdata").show(), $("#Indexdivname").show(), $("#exporthistoricaldiv").show();
                    var p = "string" == typeof result ? eval("(" + result.d + ")") : result,
                        max_size = p.length,
                        elements_per_page = 300,
                        limit = elements_per_page,
                        btn_next = document.getElementById("btn_nextDiv"),
                        btn_prev = document.getElementById("btn_prevDiv");
                    changePage(current_page), $("#btn_nextDiv").click(function () {
                        nextPage()
                    }), $("#btn_prevDiv").click(function () {
                        prevPage()
                    })
                }
            }
            else {
                $("#Historicalnodata").hide();
                $("#historydivyield").hide();
                $("#noDivdatafound").show();
            }
        },
        complete: function (a) {
            loaderhide();
        },

        error: function (a, b, c) {
            JSON.parse(a.responseText)
        }
    }), !1
}









function TotalReturnindexHistoricalData(indexname, Datestart, dateEnd) {

    if (indexname == "" || indexname == null || indexname == "0") {

        // Hide the element
        $("#historytotalindex").hide();
        document.getElementById("historytotalindex").style.display = "none";


        // Remove any class that might be forcing visibility
        $("#historytotalindex").removeClass("historyData-show show");


        // Force hide after a small delay in case another script is overriding it
        setTimeout(function () {
            $("#historytotalindex").hide();
            document.getElementById("historytotalindex").style.display = "none";
            document.getElementById("TotalReturnnodatafound").style.display = "none";

        }, 100);

        $("#TotalReturnnodatafound").hide();
        alert("Please select a valid Index name.");


        //$("#historytotalindex").css("display", "none");
        //$("#historytotalindex").hide().css("display", "none !important");
        //document.getElementById("historytotalindex").style.setProperty("display", "none", "important");

        //return window.alert("Please select valid Index name.")
    }

    //$("#historytotalindex").hide();


    /*Start 28-08-2025: Date cannot be selected more than 1 year*/
    let start = new Date(Datestart);
    let end = new Date(dateEnd);
    let timeDifference = end - start;
    const diffDays = Math.ceil(timeDifference / (1000 * 60 * 60 * 24));
    if (diffDays > 365) {
        return window.alert("Please select date range not more than 1 Year");
    }
    else if (diffDays < 0) {
        return window.alert("Start date can not be greater than End Date");
    }
    /*End 28-08-2025: Date cannot be selected more than 1 year*/

    var tableIndexNameT;
    loadershow();
    $("#TotalReturnnodatafound").hide(), $("#historytotalindex").hide();
    $("#historytotalindexexport").hide();
    var current_page = 1,

        startDate = Datestart,
        endDate = dateEnd;
    IndexMapping(indexname),
        name = selval,
        name = name.toUpperCase().trim();
    var jsonData = "{'name':'" + name + "','startDate':'" + startDate + "','endDate':'" + endDate + "','indexName':'" + indexname + "'}";
    var sendjson = {};
    sendjson.cinfo = jsonData;
    return $.ajax({
        type: "POST",
        data: JSON.stringify(sendjson),
        //data: "{'name':'" + name + "','startDate':'" + startDate + "','endDate':'" + endDate + "'}",
        url: "/BackPage/getTotalReturnIndexString",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        async: !0,
        success: function (result) {
            if (result != null && result != 0) {

                //var htmldata = "string" == typeof result.d ? eval("(" + result.d + ")") : result.d;
                var htmldata = typeof result === "string" ? JSON.parse(result.d) : result;

                  //sa ntr changes 18-12-2025
             var indexArray = ["NIFTY 50", "NIFTY MIDCAP 50", "NIFTY 500"];
            //ea ntr changes 18-12-2025


                //trHtml += '<table><thead><tr><th>DATE</th><th>OPEN</th><th>HIGH</th><th>LOW</th><th>CLOSE</th></tr></thead>';
                //trHtml += '<tbody>';
                $("#historytotalindexexport tbody").html("");
                // Nov21,2023 to replace endash('–') with hyphen('-') just only in exportFile
                var Properindexname = indexname.replace(/\u2013/g, "-");
                for (var b = 0; b < htmldata.length; b++) {
                    tableIndexNameT = htmldata[b]["Index Name"].toUpperCase();

                        //sa ntr changes 18-12-2025
                var showNTR = indexArray.includes(tableIndexNameT);
                //ea ntr changes 18-12-2025

                    //trHtml += '<tr><td>' + htmldata[f].HistoricalDate + '</td><td>' + htmldata[f].OPEN + '</td><td>' + htmldata[f].HIGH + '</td><td>' + htmldata[f].LOW + '</td><td>' + htmldata[f].CLOSE + '</td></tr>';
                    //$("#historytotalindexexport tbody").append("<tr><td>" + htmldata[b]["Index Name"].toUpperCase() + "</td><td>" + htmldata[b].Date + "</td><td>" + htmldata[b].TotalReturnsIndex + "</td></tr>");
                    //$("#historytotalindexexport tbody").append("<tr><td>" + Properindexname + "</td><td>" + htmldata[b].Date + "</td><td>" + htmldata[b].TotalReturnsIndex + "</td></tr>");

                    //sa ntr changes 18-12-2025
                var rowHtml = "<tr>"
                    + "<td>" + Properindexname + "</td>"
                    + "<td>" + htmldata[b].Date + "</td>"
                    + "<td>" + htmldata[b].TotalReturnsIndex + "</td>";

                if (showNTR ) {
                    rowHtml += "<td>" + htmldata[b].NTR_Value + "</td>";
                }

                rowHtml += "</tr>";

                $("#historytotalindexexport tbody").append(rowHtml);
                //ea ntr changes 18-12-2025

                }

                            //sa ntr changes 18-12-2025
              if (showNTR) {
                if ($("#historytotalindexexport thead th.ntr-col").length === 0) {

                    $("#historytotalindexexport thead tr")
                        .append("<th class='ntr-col'>Net Total Return Index</th>");
                }   
              }

             else {

                // HIDE → header remove
                $("#historytotalindexexport thead th:nth-child(4)").remove();
            }
            //ea ntr changes 18-12-2025


                if (tableIndexNameT == indexname || tableIndexNameT == name) {
                    tableIndexNameT = indexname
                }
                $("#historytotalindex tbody tr").remove(), $("#mobiletotalreturn").html("");
                function changePage(a) {
                    a < 1 && (a = 1), a > numPages() && (a = numPages()), $("#historytotalindex tbody tr").remove(), $("#mobiletotalreturn").html("");
                    for (var b = (a - 1) * elements_per_page; b < a * elements_per_page && b < p.length; b++) {
                        if ($(window).width() > 991)
                            $("#IndexTotalname").html(tableIndexNameT), //updated May21,2024
                                $("#datenotehistoricalTotalReturn").show(),
                               // $("#historytotalindex tbody").append("<tr><td>" + p[b].Date + "</td><td>" + p[b].TotalReturnsIndex + "</td></tr>");

                                 //sa ntr changes 18-12-2025
                            $("#historytotalindex tbody").append("<tr><td>" + p[b].Date + "</td><td>" + p[b].TotalReturnsIndex + "</td><td>" + p[b].NTR_Value + "</td></tr>");
                             //ea ntr changes 18-12-2025

                        else {
                            $("#IndexTotalname").html(tableIndexNameT); //updated May21,2024
                            $("#datenotehistoricalTotalReturn").show();

                       //sa ntr changes 18-12-2025
                        var d = "";
                        d += '<div class="fundBlock">', d += '<ul class="fundBlockIn">', d += "<li>", d += "<span>" + p[b].Date + "</span>", d += "<label>Date</label></li>", d += "<li>", d += "<span>" + p[b].TotalReturnsIndex + "</span>", d += "<label>Total Return Index</label></li>", d += "<li><span>" + p[b].NTR_Value + "</span><label>NTR Values</label></li>", d += "</ul>", d += "</div>",
                            $("#mobiletotalreturn").append(d),
                            $("#mobiletotalreturn").fadeIn()
                         //ea ntr changes 18-12-2025
                        }
                    }
                    btn_prev.style.visibility = 1 == a ? "hidden" : "visible", a == numPages() ? btn_next.style.visibility = "hidden" : btn_next.style.visibility = "visible"

                       //sa ntr changes 18-12-2025
                               if (indexArray.includes(tableIndexNameT)) {
    $("#historytotalindex th:nth-child(3), #historytotalindex td:nth-child(3)").show();
} else {
    $("#historytotalindex th:nth-child(3), #historytotalindex td:nth-child(3)").hide();
}
//ea ntr changes 18-12-2025

                }

                function numPages() {
                    return Math.ceil(max_size / elements_per_page)
                }

                function prevPage() {
                    current_page > 1 && (current_page--, changePage(current_page))
                }

                function nextPage() {
                    current_page < numPages() && (current_page++, changePage(current_page))
                }
                if ($("#historytotalindex tbody tr").remove(),
                    $("#mobiletotalreturn").html(""), "[]" == result)
                    $("#TotalReturnnodatafound").show(), $(".downloads").hide(), $(".historyData-show").hide(),
                        $("#pagehistoricalTotalreturndata").hide(),
                        $("#historytotalindex").hide();
                else {
                    $("#TotalReturnnodatafound").hide(), $(".historyData-show").show(), $("#historytotalindex").show(), $(".downloads").show(), $("#exportTotalindex").show(), $("#historytotalindex").show(), $("#pagehistoricalTotalreturndata").show(), $("#IndexTotalname").show();
                    var p = "string" == typeof result ? eval("(" + result.d + ")") : result,
                        max_size = p.length,
                        sta = 0,
                        elements_per_page = 300,
                        limit = elements_per_page,
                        btn_next = document.getElementById("btn_nextTotalReturnIndex"),
                        btn_prev = document.getElementById("btn_prevTotalReturnIndex");
                    changePage(current_page), $("#btn_nextTotalReturnIndex").click(function () {
                        nextPage()
                    }),
                        $("#btn_prevTotalReturnIndex").click(function () {
                            prevPage()
                        })
                }
            }
            else {
                $("#Historicalnodata").hide(),


                    $("#historytotalindex").hide();
                //$("#nodatafound").show();
                $("#TotalReturnnodatafound").show();

            }

        },

        complete: function (a) {
            loaderhide();
        },

        error: function (a, b, c) {

            console.log("Error: " + error);
            console.log("Status: " + status);
            console.log(xhr);
            JSON.parse(a.responseText)


            console.log(a);
        }
    }), !1
}
function loadershow() {
    $(".overlay1").show();
    $("body").css({ overflow: "inherit" });
}
function loaderhide() {
    $("body").css({ overflow: "inherit" });
    setTimeout(function () {
        $(".overlay1").fadeOut();
    }, 10);
}
function readLiveIndexFile(a, asynflag) {
    indexname = a;
    $(".btn-select-value").text(indexname);
    (flag = ""),
        "Broad Market Indices" == indexname
            ? (indexname = "bm")
            : "Sectoral Indices" == indexname
                ? (indexname = "sc")
                : "Strategy Indices" == indexname
                    ? (indexname = "st")
                    : "Thematic Indices" == indexname
                        ? (indexname = "th")
                        : "Target Maturity Index" == indexname
                            ? (indexname = "Target Maturity")
                            : "Government Securities" == indexname
                                ? (indexname = "GSec")
                                : "Corporate Bond" == indexname && (indexname = "Corporate Bond"),
        $.ajax({
            type: "GET",
            url: "https://liveindexsa.niftyindices.com/jsonfiles/LiveIndicesWatch.json",
            data: "{}",
            async: asynflag,
            cache: !1,
            dataType: "json",
            success: function (a) {
                (globaldata = a), (Sessionglobaldata = a), window.sessionStorage && sessionStorage.setItem("Sessionglobaldata", JSON.stringify(Sessionglobaldata));
                var b = $("#hdnSet").val().toUpperCase();
                b = b.split(",");
                var c = $("#hdnRedirection").val().toUpperCase();
                (c = c.split(",")), (dataLen = a.data.length);
                $("#stockwatchtable tbody tr").remove(), $("#mobilewatch").html("");
                var e = 0;
                for (i = 0; i < dataLen; i++) {
                    for (j = 0; j < b.length; j++) {
                        if (a.data[i].indexName.toUpperCase() == b[j].toUpperCase()) {
                            flag = 1;
                            break;
                        }
                        flag = 0;
                    }
                    if (1 != flag && a.data[i].indexSubType == indexname) {
                        var f = $(window).width();
                        if (
                            ((nifty50 = a.data[i].last),
                                (nifty50 = nifty50.replace(/\,/g, "")),
                                (nifty50 = parseFloat(nifty50)),
                                (nifty50close = a.data[i].previousClose),
                                (nifty50close = nifty50close.replace(/\,/g, "")),
                                (nifty50close = parseFloat(nifty50close)),
                                (Change = nifty50 - nifty50close),
                                f > 991)
                        )
                            $("#stockwatchtable").append(
                                "<tr><td><a id='indexnameurl" +
                                e +
                                "' href='/market-data/equity-stock-watch?Iname=" +
                                a.data[i].indexName +
                                "'>" +
                                a.data[i].indexName +
                                "</a></td><td class='smallchart' id='areacontainer" +
                                e +
                                "' style='height: 50px; width:80px; margin: 0 auto'></td><td><spn id='liveperchangedesk" +
                                i +
                                "' class='shareDown'>" +
                                a.data[i].percChange +
                                "%</span></td><td><span id='livechangedesk" +
                                i +
                                "' class='red'>" +
                                Change.toFixed(2) +
                                "</span></td><td>" +
                                a.data[i].low +
                                "<div class='rel' id='low" +
                                i +
                                "'></div></td><td>" +
                                a.data[i].last +
                                "</td><td>" +
                                a.data[i].high +
                                "</td><td>" +
                                a.data[i].previousClose +
                                "</td><td>" +
                                a.data[i].open +
                                "</td><td>" +
                                a.data[i].yearLow +
                                "</td><td>" +
                                a.data[i].yearHigh +
                                "</td></tr>"
                            ),
                                doSildeLiveIndexwatch(),
                                a.data[i].percChange > 0
                                    ? ($("#liveperchangedesk" + i).removeClass("shareDown"), $("#liveperchangedesk" + i).addClass("shareUp"))
                                    : ($("#liveperchangedesk" + i).removeClass("shareUp"), $("#liveperchangedesk" + i).addClass("shareDown")),
                                Change > 0 ? ($("#livechangedesk" + i).removeClass("red"), $("#livechangedesk" + i).addClass("green")) : ($("#livechangedesk" + i).removeClass("green"), $("#livechangedesk" + i).addClass("red"));
                        else {
                            var g = "";
                            (g += '<div class="fundBlock">'),
                                (g += '<ul class="fundBlockIn">'),
                                (g += "<li>"),
                                (g += '<span><a id="indexnameurl' + e + '" href="/market-data/equity-stock-watch?Iname=' + a.data[i].indexName + '" </a>' + a.data[i].indexName + "</span>"),
                                (g += "<label>Index</label></li>"),
                                (g += "<li>"),
                                (g += '<span class="smallchart" id="areacontainer' + e + '" style="height: 50px; width:80px; margin: 0 auto">'),
                                (g += "<label>Today</label>"),
                                (g += "</li>"),
                                (g += "<li>"),
                                (g += '<span id="liveperchange' + i + '" class="shareUp">' + a.data[i].percChange + "%</span>"),
                                (g += "<label>%Chng</label></li>"),
                                (g += "</ul>"),
                                (g += '<ul id="rel2' + i + '" class="fundBlockIn stockBar">'),
                                (g += "<li><span>" + a.data[i].low + "</span><label>Day Low</label></li>"),
                                (g += '<li><span class="green">' + a.data[i].last + "</span>"),
                                (g += "<label>LTP</label></li>"),
                                (g += "<li><span>" + a.data[i].high + "</span>"),
                                (g += "<label>Day HIGH</label></li></ul>"),
                                (g += '<ul class="fundBlockIn">'),
                                (g += "<li><span>" + a.data[i].previousClose + "</span>"),
                                (g += "<label>Prev Close</label></li>"),
                                (g += "<li><span>" + a.data[i].open + "</span><label>Day Open</label> </li>"),
                                (g += "<li><span>" + Change.toFixed(2) + "</span><label>chng</label></li></ul>"),
                                (g += '<ul class="fundBlockIn">'),
                                (g += "<li><span>" + a.data[i].yearLow + "</span><label>52w LOW</label></li>"),
                                (g += "<li><span>" + a.data[i].yearHigh + "</span><label>52w High</label></li></ul>"),
                                (g += "</div>"),
                                $("#mobilewatch").append(g);
                            doSildeLiveIndexwatch_mob("rel2" + i),
                                a.data[i].percChange > 0
                                    ? ($("#liveperchange" + i).removeClass("shareDown"), $("#liveperchange" + i).addClass("shareUp"))
                                    : ($("#liveperchange" + i).removeClass("shareUp"), $("#liveperchange" + i).addClass("shareDown"));
                        }
                        e += 1;
                    }
                }
                $("#stockwatchtable tbody tr").hide();
                var k = 1;
                for (i = 0; i < dataLen; i++)
                    if (a.data[i].indexSubType == indexname) {
                        for (j = 0; j < c.length; j++)
                            if (a.data[i].indexName == c[j]) {
                                var l = $("#stockwatchtable tbody tr:nth-child(" + k + ")");
                                l.find("td:nth-child(1) a").attr("href", "javascript:void(0)");
                                l.find("td:nth-child(1) a").addClass("removeRedirect");
                            }
                        for (j = 0; j < b.length; j++) {
                            if (a.data[i].indexName.toUpperCase() == b[j].toUpperCase()) {
                                flag = 1;
                                break;
                            }
                            flag = 0;
                        }
                        k++;
                    }
                if ((f > 991 ? loadmoretable() : loadmoremobile(), incIndex <= dataLen && (incIndex += 15) > dataLen)) {
                    var m = dataLen - incIndex;
                    m > 0 && (incIndex += m);
                }
                (strdate = a.data[0].timeVal), refreshDate(strdate), loaderhide();
            },
            complete: function (a) {
                loaderhide();
            },
            error: function (a) { },
        });
}
function readETFFile() {
    $.ajax({
        type: "GET",
        url: "https://liveindexsa.niftyindices.com/jsonfiles/ETF.json",
        data: "{}",
        async: !1,
        cache: !1,
        dataType: "json",
        success: function (a) {
            a.data.length;
            (Sessionglobaldata = a), window.sessionStorage && sessionStorage.setItem("Sessionglobaldata", JSON.stringify(Sessionglobaldata)), $("#stockwatchtable tbody tr").remove(), $("#mobilewatch").html("");
            var d = 0;
            for (i = ETFindex; i < a.data.length; i++) {
                var e = $(window).width();
                if (e > 991)
                    $("#stockwatchtable").append(
                        "<tr><td>" +
                        a.data[i].symbol +
                        "</td><td>" +
                        a.data[i].assets +
                        "</td><td class='smallchart' id='areacontainer" +
                        d +
                        "' style='height: 50px; width:80px; margin: 0 auto'></td><td><span id='eftperchangedesk" +
                        i +
                        "' class='shareUp'>" +
                        a.data[i].per +
                        "%</td><td><span id='etfchangedesk" +
                        i +
                        "' class='red'>" +
                        a.data[i].chn +
                        "</td><td>" +
                        a.data[i].low +
                        "<div class='rel' id='low" +
                        i +
                        "'></div></td><td>" +
                        a.data[i].ltP +
                        "</td><td>" +
                        a.data[i].high +
                        "</td><td>" +
                        a.data[i].open +
                        "</td><td>" +
                        a.data[i].wklo +
                        "</td><td>" +
                        a.data[i].wkhi +
                        "</td></tr>"
                    ),
                        doSilderETF(),
                        a.data[i].per > 0
                            ? ($("#eftperchangedesk" + i).removeClass("shareDown"), $("#eftperchangedesk" + i).addClass("shareUp"))
                            : ($("#eftperchangedesk" + i).removeClass("shareUp"), $("#eftperchangedesk" + i).addClass("shareDown")),
                        a.data[i].chn > 0 ? ($("#etfchangedesk" + i).removeClass("red"), $("#etfchangedesk" + i).addClass("green")) : ($("#etfchangedesk" + i).removeClass("green"), $("#etfchangedesk" + i).addClass("red"));
                else {
                    var f = "";
                    (f += '<div class="fundBlock">'),
                        (f += '<ul class="fundBlockIn">'),
                        (f += "<li>"),
                        (f += "<span>" + a.data[i].symbol + "</span>"),
                        (f += "<label>Symbol</label></li>"),
                        (f += "<li>"),
                        (f += '<span class="smallchart" id="areacontainer' + i + '" style="height: 50px; width:80px; margin: 0 auto"></span>'),
                        (f += "<label>Today</label>"),
                        (f += "</li>"),
                        (f += "<li>"),
                        (f += "<span>" + a.data[i].assets + "</span>"),
                        (f += "<label>Assets</label></li>"),
                        (f += "</ul>"),
                        (f += '<ul id="rel2' + i + '" class="fundBlockIn stockBar">'),
                        (f += "<li><span>" + a.data[i].low + "</span><label>Day Low</label></li>"),
                        (f += '<li><span class="green">' + a.data[i].ltP + "</span>"),
                        (f += "<label>LTP</label></li>"),
                        (f += "<li><span>" + a.data[i].high + "</span>"),
                        (f += "<label>Day HIGH</label></li></ul>"),
                        (f += '<ul class="fundBlockIn">'),
                        (f += '<li><span id="etfperchange' + i + '" class="shareUp">' + a.data[i].per + "%</span>"),
                        (f += "<label>%Chng</label></li>"),
                        (f += "<li><span>" + a.data[i].open + "</span><label>Day Open</label> </li>"),
                        (f += "<li><span>" + a.data[i].chn + "</span><label>chng</label></li></ul>"),
                        (f += '<ul class="fundBlockIn">'),
                        (f += "<li><span>" + a.data[i].wklo + "</span><label>52w LOW</label></li>"),
                        (f += "<li><span>" + a.data[i].wkhi + "</span><label>52w High</label></li></ul>"),
                        (f += "</div>"),
                        $("#mobilewatch").append(f);
                    doSilderETF_mob("rel2" + i),
                        a.data[i].per > 0 ? ($("#etfperchange" + i).removeClass("shareDown"), $("#etfperchange" + i).addClass("shareUp")) : ($("#etfperchange" + i).removeClass("shareUp"), $("#etfperchange" + i).addClass("shareDown"));
                }
                d += 1;
            }
            (ETFindex += 15), e > 991 ? loadmoretable() : loadmoremobile(), (strdate = a.time), refreshDate(strdate);
        },
        complete: function (a) {
            loaderhide();
        },
        error: function (a) { },
    });
}
function exportTableToCSV(a, b) {
    function j(a) {
        return a.get().join(f).split(f).join(h).split(e).join(g);
    }
    function k(a, b) {
        var c = $(b),
            d = c.find("td");
        return d.length || (d = c.find("th")), d.map(l).get().join(e);
    }
    function l(a, b) {
        return $(b).text().replace('"', '""');
    }
    var c = a.find("tr:has(th)"),
        d = a.find("tr:has(td)"),
        e = String.fromCharCode(11),
        f = String.fromCharCode(0),
        g = '","',
        h = '"\r\n"',
        i = '"';
    (i += j(c.map(k))),
        (i += h),
        (i += j(d.map(k)) + '"'),
        (csvData = "data:application/csv;charset=utf-8," + encodeURIComponent(i)),
        window.navigator.msSaveBlob ? window.navigator.msSaveOrOpenBlob(new Blob([i], { type: "text/plain;charset=utf-8;" }), "csvname.csv") : $(this).attr({ download: b, href: csvData, target: "_blank" });
}
function HideData() {
    $(".noData").hide(),
        $("#tblreport").show();
    $("#Indexname").hide();
}
function HolidayControl() {
    $("#exportholidaycalender").on("click", function (a) {
        exportTableToCSV.call(this, $("#HolidayList"), "HolidaycalenderData.csv");
    });
}
function submit_calender() {
    var b,
        c,
        a = $("#datepickerFromholiday").datepicker("getDate");
    null == a ? (b = $("#Hiddendatepickerfrom").val()) : ((b = $.datepicker.formatDate("mm/dd/yy", a)), $("#Hiddendatepickerfrom").val(b)),
        $(".dateHolderyear").html(b.year),
        $(".dateHoldercurdate").html(b),
        $(".dateHoldermonth").html(b.month);
    var d = $("#datepickerToholiday").datepicker("getDate");
    null == d ? (c = $("#Hiddendatepickerfrom").val()) : ((c = $.datepicker.formatDate("mm/dd/yy", d)), $("#HiddendatepickerTo").val(c));
    var e = Date.parse(b),
        f = Date.parse(c);
    Math.floor((f - e) / 864e5);
    if (("" == b && ((b = new Date()), (b = b.format("MM/dd/yyyy")), $("#Hiddendatepickerfrom").val(b)), "" == c && ((c = new Date()), (c = c.format("MM/dd/yyyy")), $("#HiddendatepickerTo").val(c)), "" != b && "" != c))
        return !(e > f) || (alert("Start date cannot be greater than end date"), !1);
}
function ResetDateValue() {
    var a = $("#Hiddendatepickerfrom").val(),
        b = ["JAN", "FEB", "MAR", "APR", "MAY", "JUNE", "JULY", "AUG", "SEP", "OCT", "NOV", "DEC"];
    $("#dateHolderyear").html(a.substr(6, 4)), $("#dateHoldercurdate").html(a.substr(3, 2)), $("#dateHoldermonth").html(b[a.substr(0, 1)]);
    var c = $("#HiddendatepickerTo").val();
    $("#dateHolderToyear").html(c.substr(6, 4)), $("#dateHolderTocurdate").html(c.substr(3, 2)), $("#dateHolderTomonth").html(b[c.substr(0, 1)]);
}
function submit_ArchivesMonthlyReports() {
    var flag = $("#hdnMonthYear").val();
    var optionSelected = $("#ArchiveDailyReport").val();
    var flag2 = $("#HiddendatepickerfromMonthly").val();
    if ((flag == null || flag == "") && (optionSelected != "0" || optionSelected != "1")) {
        var date = new Date();
        var monthArray = ["", "JAN", "FEB", "MAR", "APR", "MAY", "JUNE", "JULY", "AUG", "SEP", "OCT", "NOV", "DEC"];
        var month = monthArray[date.getMonth() + 1];
        var year = date.getFullYear();
        $("#hdnMonthYear").val(month + "" + year);
    } else if ((flag2 == null || flag2 == "") && optionSelected == "1") {
        var date = new Date();
        var newDate = date.format("MM/dd/yyyy");
        $("#HiddendatepickerfromMonthly").val(newDate);
    }
    var b,
        c,
        a = $("#datepickerFromDailyReport").datepicker("getDate");
    (b = $.datepicker.formatDate("mm/dd/yy", a)), $("#HiddendatepickerfromMonthly").val(b);
    var d = Date.parse(b),
        e = Date.parse(c);
    Math.floor((e - d) / 864e5);
    if (("" == b && ((b = new Date()), (b = b.toLocaleDateString("en-GB")), $("#HiddendatepickerfromMonthly").val(b)), "" != b && "" != c)) return !(d > e) || (alert("Start date cannot be greater than end date"), !1);
}
function SectorialData() {
    return (
        (Idname = $("#hdnSet").val()),
        (Idname = Idname.trim()),
        $.ajax({
            type: "POST",
            data: "{'indexname':'" + Idname + "'}",
            url: "/BackPage/BindSectrialData",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            async: !0,
            success: function (a) {
                0 == a.length ? (isSuccess = !1) : (isSuccess = !0);
            },
            error: function (a) { },
        }),
        !1
    );
}
function ReturnProfile(a, b, c) {
    var d = "";
    "Broad Market Indices" == a ? (a = "bm") : "Sectoral Indices" == a ? (a = "sc") : "Strategy Indices" == a ? (a = "st") : "Thematic Indices" == a && (a = "th"),
        $.ajax({
            type: "POST",
            data: "{'name':'" + a + "','startDate':'" + b + "','endDate':'" + c + "'}",
            url: "/BackPage/ReturnProfile",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            async: !0,
            success: function (b) {
                $("#stockwatchtable tbody tr").remove(), $("#mobilewatch").html("");
                var e = $("#hdnSet").val().toUpperCase();
                for (e = e.split(","), i = 0; i < b.length; i++) {
                    for (j = 0; j < e.length; j++) {
                        if (b[i].indexName == e[j]) {
                            d = 1;
                            break;
                        }
                        d = 0;
                    }
                    if (1 != d && b[i].indexType == a) {
                        var f = $(window).width(),
                            g = b.length;
                        b[0].close, b[g].close, b[g].close;
                        if (f > 991)
                            $("#stockwatchtable").append(
                                "<tr><td><a href='/market-data/equity-stock-watch?Iname=" +
                                b.data[i].indexName +
                                "'>" +
                                b.data[i].indexName +
                                "</a></td><td class='smallchart' id='areacontainer" +
                                i +
                                "' style='height: 50px; width:80px; margin: 0 auto'></td><td><spn id='liveperchangedesk" +
                                i +
                                "' class='shareDown'>" +
                                b.data[i].percChange +
                                "%</span></td><td><span id='livechangedesk" +
                                i +
                                "' class='red'>" +
                                Change.toFixed(2) +
                                "</span></td><td>" +
                                b.data[i].low +
                                "<div class='rel' id='low" +
                                i +
                                "'></div></td><td>" +
                                b.data[i].last +
                                "</td><td>" +
                                b.data[i].high +
                                "</td><td>" +
                                b.data[i].previousClose +
                                "</td><td>" +
                                b.data[i].open +
                                "</td><td>" +
                                b.data[i].yearLow +
                                "</td><td>" +
                                b.data[i].yearHigh +
                                "</td></tr>"
                            );
                        else {
                            var k = "";
                            (k += '<div class="fundBlock">'),
                                (k += '<ul class="fundBlockIn">'),
                                (k += "<li>"),
                                (k += '<span><a href="/market-data/equity-stock-watch?Iname=' + b.data[i].indexName + '" </a>' + b.data[i].indexName + "</span>"),
                                (k += "<label>Index</label></li>"),
                                (k += "<li>"),
                                (k += '<span class="smallchart" id="areacontainer' + i + '" style="height: 50px; width:80px; margin: 0 auto">'),
                                (k += "<label>Today</label>"),
                                (k += "</li>"),
                                (k += "<li>"),
                                (k += '<span id="liveperchange' + i + '" class="shareUp">' + b.data[i].percChange + "%</span>"),
                                (k += "<label>%Chng</label></li>"),
                                (k += "</ul>"),
                                (k += '<ul id="rel2' + i + '" class="fundBlockIn stockBar">'),
                                (k += "<li><span>" + b.data[i].low + "</span><label>Day Low</label></li>"),
                                (k += '<li><span class="green">' + b.data[i].last + "</span>"),
                                (k += "<label>LTP</label></li>"),
                                (k += "<li><span>" + b.data[i].high + "</span>"),
                                (k += "<label>Day HIGH</label></li></ul>"),
                                (k += '<ul class="fundBlockIn">'),
                                (k += "<li><span>" + b.data[i].previousClose + "</span>"),
                                (k += "<label>Prev Close</label></li>"),
                                (k += "<li><span>" + b.data[i].open + "</span><label>Day Open</label> </li>"),
                                (k += "<li><span>" + Change.toFixed(2) + "</span><label>chng</label></li></ul>"),
                                (k += '<ul class="fundBlockIn">'),
                                (k += "<li><span>" + b.data[i].yearLow + "</span><label>52w LOW</label></li>"),
                                (k += "<li><span>" + b.data[i].yearHigh + "</span><label>52w High</label></li></ul>"),
                                (k += "</div>"),
                                $("#mobilewatch").append(k);
                        }
                    }
                }
            },
            error: function (a) { },
        });
}
function chkOfflineIndex() {
    $.expr[":"].textEquals = function (a, b, c) {
        return (
            (de = $(a).text().toUpperCase().replace(/\s/g, "")),
            $(a)
                .text()
                .toUpperCase()
                .replace(/\s/g, "")
                .replace(/\(|\)/g, "")
                .match("^" + c[3] + "$")
        );
    };
    var a = $("#removeind").val().toUpperCase();
    for (a = a.split(","), i = 0; i < a.length; i++) (dec = a[i].replace(/\s/g, "")), $("#ddlHeatMap li:textEquals(" + dec + ")").addClass("offlineInd");
    $(".offlineInd").hide();
}
function chkOfflineIndexTicker() {
    $.expr[":"].textEquals = function (a, b, c) {
        return (
            (de = $(a).text().toUpperCase().replace(/\s/g, "")),
            $(a)
                .text()
                .toUpperCase()
                .replace(/\s/g, "")
                .replace(/\(|\)/g, "")
                .match("^" + c[3] + "$")
        );
    };
    var a = $("#removeind").val().toUpperCase();
    for (a = a.split(","), i = 0; i < a.length; i++) (dec = a[i].replace(/\s/g, "")), $("#ddlHeatMap li:textEquals(" + dec + ")").addClass("offlineInd");
    $(".offlineInd").hide();
}
function chkOfflineHeatmapIndex() {
    $.expr[":"].textEquals = function (a, b, c) {
        return (
            (de = $(a).text().toUpperCase().replace(/\s/g, "")),
            $(a)
                .text()
                .toUpperCase()
                .replace(/\s/g, "")
                .replace(/\(|\)/g, "")
                .match("^" + c[3] + "$")
        );
    };
    var a = $("#removeind").val().toUpperCase();
    for (a = a.split(","), i = 0; i < a.length; i++) (dec = a[i].replace(/\s/g, "")), $("#ddlHeatmapdetail li:textEquals(" + dec + ")").addClass("offlineInd");
    $(".offlineInd").hide();
}
function chkOfflineTotalReturnIndexDetail() {
    $.expr[":"].textEquals = function (a, b, c) {
        return (
            (de = $(a).text().toUpperCase().replace(/\s/g, "")),
            $(a)
                .text()
                .toUpperCase()
                .replace(/\s/g, "")
                .replace(/\(|\)/g, "")
                .match("^" + c[3] + "$")
        );
    };
    var a = $("#removeind").val().toUpperCase();
    for (a = a.split(","), i = 0; i < a.length; i++) (dec = a[i].replace(/\s/g, "")), $("#ddlHistoricaltotalindex li:textEquals(" + dec + ")").addClass("offlineInd");
    $(".offlineInd").hide();
}
function chkOfflinePepbdivyieldDetail() {
    $.expr[":"].textEquals = function (a, b, c) {
        return (
            (de = $(a).text().toUpperCase().replace(/\s/g, "")),
            $(a)
                .text()
                .toUpperCase()
                .replace(/\s/g, "")
                .replace(/\(|\)/g, "")
                .match("^" + c[3] + "$")
        );
    };
    var a = $("#removeind").val().toUpperCase();
    for (a = a.split(","), i = 0; i < a.length; i++) (dec = a[i].replace(/\s/g, "")), $("#ddlHistoricalDivYield li:textEquals(" + dec + ")").addClass("offlineInd");
    $(".offlineInd").hide();
}
function chkofflinetopgainersloosers() {
    $.expr[":"].textEquals = function (a, b, c) {
        return (
            (de = $(a).text().toUpperCase().replace(/\s/g, "")),
            $(a)
                .text()
                .toUpperCase()
                .replace(/\s/g, "")
                .replace(/\(|\)/g, "")
                .match("^" + c[3] + "$")
        );
    };
    var a = $("#removeind").val().toUpperCase();
    for (a = a.split(","), i = 0; i < a.length; i++) (dec = a[i].replace(/\s/g, "")), $("#ddlStocksGainers li:textEquals(" + dec + ")").addClass("offlineInd");
    $(".offlineInd").hide();
}
function loadmoreHeatmaptable() {
    $("#stockHeatmaptable tbody tr").hide();
    var a = $("#stockHeatmaptable tbody tr").length,
        b = 51;
    a < b && (b = a),
        $("#stockHeatmaptable tbody tr:lt(" + b + ")").show(),
        $("#loadmore").click(function (c) {
            var currentLength = $("#stockHeatmaptable tr:visible").length;
            loadershow(),
                c.preventDefault(),
                (b = b + 51 <= a ? b + 50 : a),
                $("tr:lt(" + (b + 1) + ")").show(),
                currentLength >= a ? $("#loadmore").hide() : $("#loadmore").show(),
                typeof loadmoresortele !== typeof undefined ? SortArray(loadmoresortele) : "",
                loaderhide();
        }),
        b + 1 >= a ? $("#loadmore").hide() : $("#loadmore").show(),
        loaderhide();
}
function HeatmapDetail(a) {
    $("#loadmore").show(),
        (a = a.toUpperCase().trim()),
        (a = a.trim()),
        $.ajax({
            type: "GET",
            url: "https://liveindexsa.niftyindices.com/jsonfiles/HeatmapDetail/FinalHeatmap" + a + ".json",
            data: "{}",
            async: !0,
            cache: !1,
            dataType: "json",
            success: function (a) {
                for ($("#stockHeatmaptable tbody tr").remove(), $("#mobilewatch").html(""), i = 0; i < a.length; i++) {
                    var c = $(window).width();
                    var num = 0.0;
                    if (parseFloat(a[i].pointchange) == 0) {
                        a[i].pointchange = num.toFixed(2);
                    }
                    if (parseFloat(a[i].perchange) == 0) {
                        a[i].perchange = num.toFixed(2);
                    }
                    if (c > 991) {
                        $("#stockHeatmaptable").append(
                            "<tr><td>" +
                            a[i].symbol +
                            "</td><td class='leftAlign'>" +
                            a[i].sector +
                            "</td><td><span id='pricechange" +
                            i +
                            "' class=''>" +
                            a[i].iislPercChange +
                            "%</td><td><span id='priceperchange" +
                            i +
                            "' class=''>" +
                            a[i].iislPtsChange +
                            "</td><td><span id='indexperchange" +
                            i +
                            "' class=''>" +
                            a[i].perchange +
                            "</td><td><span id='indexchange" +
                            i +
                            "' class=''>" +
                            a[i].pointchange +
                            "</td></tr>"
                        );
                        if (parseFloat(a[i].iislPercChange) > 0.0) {
                            $("#pricechange" + i).removeClass("shareDown");
                            $("#pricechange" + i).addClass("shareUp");
                        } else if (parseFloat(a[i].iislPercChange) < 0.0) {
                            $("#pricechange" + i).removeClass("shareUp");
                            $("#pricechange" + i).addClass("shareDown");
                        } else {
                            $("#pricechange" + i).removeClass("shareUp");
                            $("#pricechange" + i).removeClass("shareDown");
                        }
                        if (parseFloat(a[i].iislPtsChange) > 0.0) {
                            $("#priceperchange" + i).removeClass("red");
                            $("#priceperchange" + i).addClass("green");
                        } else if (parseFloat(a[i].iislPtsChange) < 0.0) {
                            $("#priceperchange" + i).removeClass("green");
                            $("#priceperchange" + i).addClass("red");
                        } else {
                            $("#priceperchange" + i).removeClass("green");
                            $("#priceperchange" + i).removeClass("red");
                        }
                        if (parseFloat(a[i].iislPercChange) > 0.0 && parseFloat(a[i].iislPtsChange) > 0.0) {
                            if (parseFloat(a[i].pointchange) > 0.0) {
                                $("#indexchange" + i).removeClass("red");
                                $("#indexchange" + i).addClass("green");
                            }
                            if (parseFloat(a[i].perchange) > 0.0) {
                                $("#indexperchange" + i).removeClass("shareDown");
                                $("#indexperchange" + i).addClass("shareUp");
                            }
                        } else if (parseFloat(a[i].iislPercChange) < 0.0 && parseFloat(a[i].iislPtsChange) < 0.0) {
                            if (parseFloat(a[i].pointchange) < 0.0) {
                                $("#indexchange" + i).addClass("red");
                                $("#indexchange" + i).removeClass("green");
                            }
                            if (parseFloat(a[i].perchange) < 0.0) {
                                $("#indexperchange" + i).addClass("shareDown");
                                $("#indexperchange" + i).removeClass("shareUp");
                            }
                        }
                        if (parseFloat(a[i].pointchange) == 0.0) {
                            $("#indexchange" + i).removeClass("green");
                            $("#indexchange" + i).removeClass("red");
                        }
                        if (parseFloat(a[i].perchange) == 0.0) {
                            $("#indexperchange" + i).removeClass("shareUp");
                            $("#indexperchange" + i).removeClass("shareDown");
                        }
                    } else {
                        var d = "";
                        (d += '<div class="fundBlock">'),
                            (d += '<ul class="fundBlockIn">'),
                            (d += "<li>"),
                            (d += "<span>" + a[i].symbol + "</span>"),
                            (d += "<label>Symbol</label></li>"),
                            (d += "<li>"),
                            (d += "<span>" + a[i].sector + "</span>"),
                            (d += "<label>Symbol</label></li>"),
                            (d += "<li>"),
                            (d += '<span id="per' + i + '" class="shareUp">' + a[i].iislPercChange + "%</span>"),
                            (d += "<label>Price<br>%Chng</label></li>"),
                            (d += "</ul>"),
                            (d += '<ul class="fundBlockIn">'),
                            (d += '<li><span id="change>' + i + '" class="green">' + a[i].iislPtsChange + "</span><label>Price<br>chng</label></li>"),
                            (d += "<li>"),
                            (d += '<span id="perchange' + i + '" class="shareUp">' + a[i].perchange + "%</span>"),
                            (d += "<label>Index<br>%Chng</label></li>"),
                            (d += '<li><span id="pointchange>' + i + '" class="green">' + a[i].pointchange + "</span><label>Index<br>chng</label></li></ul>"),
                            (d += "</div>"),
                            $("#mobilewatchHeatmap").append(d);
                        if (parseFloat(a[i].iislPercChange) > 0.0) {
                            $("#per" + i).removeClass("shareDown");
                            $("#per" + i).addClass("shareUp");
                        } else if (parseFloat(a[i].iislPercChange) < 0.0) {
                            $("#per" + i).removeClass("shareUp");
                            $("#per" + i).addClass("shareDown");
                        } else {
                            $("#per" + i).removeClass("shareUp");
                            $("#per" + i).removeClass("shareDown");
                        }
                        if (parseFloat(a[i].iislPtsChange) > 0.0) {
                            $("#change" + i).removeClass("red");
                            $("#change" + i).addClass("green");
                        } else if (parseFloat(a[i].iislPtsChange) < 0.0) {
                            $("#change" + i).removeClass("green");
                            $("#change" + i).addClass("red");
                        } else {
                            $("#change" + i).removeClass("red");
                            $("#change" + i).removeClass("green");
                        }
                        if (parseFloat(a[i].iislPercChange) > 0.0 && parseFloat(a[i].iislPtsChange) > 0.0) {
                            if (parseFloat(a[i].pointchange) > 0.0) {
                                $("#pointchange" + i).removeClass("red");
                                $("#pointchange" + i).addClass("green");
                            }
                            if (parseFloat(a[i].perchange) > 0.0) {
                                $("#perchange" + i).removeClass("shareDown");
                                $("#perchange" + i).addClass("shareUp");
                            }
                        } else if (parseFloat(a[i].iislPercChange) < 0.0 && parseFloat(a[i].iislPtsChange) < 0.0) {
                            if (parseFloat(a[i].pointchange) < 0.0) {
                                $("#pointchange" + i).addClass("red");
                                $("#pointchange" + i).removeClass("green");
                            }
                            if (parseFloat(a[i].perchange) < 0.0) {
                                $("#perchange" + i).addClass("shareDown");
                                $("#perchange" + i).removeClass("shareUp");
                            }
                        }
                        if (parseFloat(a[i].pointchange) == 0.0) {
                            $("#pointchange" + i).removeClass("green");
                            $("#pointchange" + i).removeClass("red");
                        }
                        if (parseFloat(a[i].perchange) == 0.0) {
                            $("#perchange" + i).removeClass("shareDown");
                            $("#perchange" + i).removeClass("shareUp");
                        }
                    }
                }
                $("#stockHeatmaptable tbody tr").hide(), c > 991 ? loadmoreHeatmaptable() : loadmoremobileheatmap(), (strdate = a[0].time), refreshDate(strdate);
            },
            error: function (a) { },
        });
}
function loadmoremobileheatmap() {
    $(".fundBlock").hide();
    var a = $(".fundBlock").length,
        b = 5;
    $(".fundBlock:lt(" + b + ")").show(),
        $(".LoadMore").click(function (c) {
            c.preventDefault(), (b = b + 6 <= a ? b + 5 : a), $(".fundBlock:lt(" + b + ")").show(), b >= a && $(".LoadMore").hide();
        }),
        b >= a && $(".LoadMore").hide();
}
var hiddenDate = "",
    resetDate;
function getIndex() {
    //loadershow();
    //  GetReturnProfileHoliday();    // 04-06-2018
    //Return profile on load
    var a = $(".btn-select-value").text();
    var b = $(".btn-select-table").text();

    getReturnsProfile(a, false, b);

    //Return profile on selection
    $("#ddlReturnprofile li").click(function () {
        /* loadershow();*/
        //var a = $(this).text();
        var a = $(this).text();
        var b = $(".btn-select-table").text();
        getReturnsProfile(a, true, b);
    });
    $("#ddltrhr li").click(function () {
        /*loadershow();*/
        var b = $(this).text();
        var a = $(".btn-select-value").text();
        getReturnsProfile(a, true, b);
    });

    // loaderhide();
    //$("#ddltrhr li").click(function () {
    //    //loadershow();
    //    var b = $('#ddltrhr li.selected').text();
    //    var a = $(".btn-select-value").text();
    //    getReturnsProfile(a, true, b);
    //    alert(a, b);
    //});
    //Reset Date to today's Date
    //$("#reset_button").click(function () { //Working , not using for time being
    //    $('#datepickerReturnProfile').datepicker('setDate', new Date());
    //});
}
function submitReturnProfileDate() {
    // 05-06-2017
    loadershow();
    var indexType = $("#selectedinReturnProfile").text(); // index type
    var table = $("#selectedtable").text();
    hiddenDate = $("#datepickerReturnProfile").datepicker("getDate");
    hiddenDate = $.datepicker.formatDate("yy-mm-dd", hiddenDate);
    if (indexType != "") {
        getReturnsProfile(indexType, true, table);
    }
    /*    loaderhide();*/
}
function ResetReturnProfileDate() {
     /* ---------- Index dropdown reset ---------- */
  $("#selectedinReturnProfile").text("Broad Market Indices");
  $("#indexdropdown").val("bm");

  $("#ddlReturnprofile li").removeClass("active selected");
  $("#ddlReturnprofile li#bm").addClass("active selected");


  /* ---------- Return type dropdown reset ---------- */
  $("#selectedtable").text("Total Return");
  $("#indexdropdown2").val("TR");

  $("#ddltrhr li").removeClass("active selected");
  $("#ddltrhr li#TR").addClass("active selected");

   isResettingReturnProfile = true;

  var maxDate = $("#datepickerReturnProfile")
      .datepicker("option", "maxDate") || new Date();

  $("#datepickerReturnProfile").datepicker("setDate", maxDate);

  isResettingReturnProfile = false;

  submitReturnProfileDate();
}
function importResearchPapers() {

    loadershow();
    //var page = 0;
    var selectedIndex = $("#inputResearchPaper").val();
    pageSize = 8;

    var pageCount = $("#ResearchPaper").length / pageSize;

    //for (var i = 0 ; i < pageCount; i++) {
    //    debugger;
    //    $("#pagepaperdata").append('<li><a href="#">' + (i + 1) + '</a></li> ');
    //}
    $("#pagepaperdata li").first().find("a").addClass("prevArrow")
    showPage = function (page) {

        $("#ResearchPaper").hide();
        $("#ResearchPaper").each(function (n) {
            if (n >= pageSize * (page - 1) && n < pageSize * page)
                $(this).show();
        });
    }

    var jsonData = "{'selectedIndex':'" + selectedIndex + "'}";
    var sendjson = {};
    sendjson.cinfo = jsonData;
    //function showPage(page) {
    //    for (i = 0; i >= page;i++)
    //    {
    //        $('#tblreport1 .post:not(#ResearchPaper' + page + ')').hide();
    //    }

    //    $('#tblreport1 .post#ResearchPaper' + page).show();
    //}

    //function prevPage() {
    //    if (page == 1) {
    //        page = $('#tblreport1 .post').length;
    //    } else {
    //        page--;
    //    }
    //    showPage(page);
    //}

    //function nextPage() {
    //    if (page == $('#tblreport1 .post').length) {
    //        page = 1;
    //    } else {
    //        page++;
    //    }
    //    showPage(page);
    //}
    $.ajax({
        type: "POST",
        url: "/BackPage/getResearchPaper",
        data: JSON.stringify(sendjson),
        async: true,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {

            console.log("AJAX Success:", data);

            var mobileViewHtml = "";
            var desktopviewHtml = "";
            var browserWidth = $(window).width();
            $("#tblreport1").html("");

            // Check if data.d exists and is not "false"
            if (data != "false") {
                $("#show1").hide();
                var researchPaperList = data;

                for (var i = 0; i < researchPaperList.length; i++) {

                    desktopviewHtml = "<div id= 'ResearchPaper' class='post'>";
                    desktopviewHtml += "<div style='padding-bottom: 11px;' id='divResearchPaperType'>";
                    desktopviewHtml += "<h3 id='researchPaperTypeTitle'>" + researchPaperList[i].category + "</h3></div>";
                    desktopviewHtml += "<div class='col-md-12' style='padding-bottom:2rem;'><div class='dailyUpdates reportDate'><ul class='downloads'>";
                    for (var j = 0; j < researchPaperList[i].downloadUrl.length; j++) {
                        //  desktopviewHtml += "<li><a id='researchArchiveLinks' href=" + researchPaperList[i].downloadUrl[j] + ">"+researchPaperList[i].documentname[j]+"</a>"+"  " +researchPaperList[i].formatdate+"</li>";
                        desktopviewHtml += "<li class='clearfix'><div class='col-xs-12 col-sm-8'><a id='researchArchiveLinks' target='_blank' href=" + researchPaperList[i].downloadUrl[j] + ">" + researchPaperList[i].documentname[j] + "</a></div>" + "<div class='col-xs-12 col-sm-4 mnthDate'>" + researchPaperList[i].formatdate[j] + "</div></li>";
                    }


                    desktopviewHtml += "</ul></div></div></div>";
                    $("#tblreport1").append(desktopviewHtml);

                }
                showPage(1);

                //$('#btn_prev').click(prevPage);
                //$('#btn_next').click(nextPage);

                HideData();



                //$("#pagepaperdata li a").click(function () {
                //    $("#pagepaperdata li a").removeClass("prevArrow");
                //    $(this).addClass("prevArrow");
                //    showPage(parseInt($(this).text()))
                //});
                $("#tblreport1").show();
                $(".historyData-show").show();
            }

            else {

                $("#tblreport1").hide();
                $("#researchPapertID").text("No Data Found");
                var oldsrc = "../images/historical_data.png";
                $('#ArchiveImage[src="' + oldsrc + '"]').attr("src", "../images/error404.png");
                $("#show1").show();
                $("#pagepaperdata").hide();

            }
            loaderhide();
        },
        error: function (a) {
            console.log(a)
        }
    });

}



function getReturnsProfile(typeOfIndex, asynflag, typeOfTable1) {

    loadershow();
    $("#divNotefixincome").hide();
    var returnProfileDate;
    /*    var date = new Date();*/
    var date = $("#datepickerReturnProfile").datepicker("getDate");

    var day = date.getDate();
    var month = date.getMonth() + 1;
    var year = date.getFullYear();

    if (hiddenDate != "") {
        returnProfileDate = hiddenDate;
    } else {
        returnProfileDate = "" + year + "/" + month + "/" + day + "";
    }
    var typeOfIndexSymbol = "";
    switch (typeOfIndex) {
        case "Broad Market Indices":
            typeOfIndexSymbol = "bm";
            $("#divNotefixincome").hide();
            break;
        case "Sectoral Indices":
            typeOfIndexSymbol = "sc";
            $("#divNotefixincome").hide();
            break;
        case "Strategy Indices":
            typeOfIndexSymbol = "st";
            $("#divNotefixincome").hide();
            break;
        case "Thematic Indices":
            typeOfIndexSymbol = "th";
            $("#divNotefixincome").hide();
            break;
        case "Fixed Income Indices":
            typeOfIndexSymbol = "fi";
            $("#divNotefixincome").show();
            break;
        default:
            console.log("Not Matching Type =" + typeOfIndex);
            break;
    }
    var typeOfTableSymbol = "";
    switch (typeOfTable1) {
        case "Total Return":
            typeOfTableSymbol = "TR";
            break;
        case "Price Return":
            typeOfTableSymbol = "HR";
            break;
        default:

            console.log("Not Matching Type =" + typeOfTable1);
            break;
    }
    if (typeOfTable1 == "Total Return" && typeOfIndex == "Fixed Income Indices") {
        typeOfTableSymbol = "HR";
        typeOfTable1 = "Price Return";
    }
    //New Line nov2,23
    var jsonData = "{'indexTypeName': '" + typeOfIndexSymbol + "','currentTradingDate': '" + returnProfileDate + "','tablename':'" + typeOfTable1 + "'}";
    var sendjson = {};
    sendjson.cinfo = jsonData;
    console.log("JSON Data: ", jsonData);
    $.ajax({

        type: "POST",
        //url: "/BackPage.aspx/getReturnsNew",
        url: "/BackPage/getReturnsNew",
        //data: "{'indexTypeName': '" + typeOfIndexSymbol + "','currentTradingDate': '" + returnProfileDate + "','tablename':'" + typeOfTable1 + "'}",
        data: JSON.stringify(sendjson),
        async: asynflag,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            console.log(data)
            console.log("Data Type: ", typeof data);

            
//sa vishal return profile issue changes
	console.log("RAW:", data);

const payload = (data && typeof data === "object" && "d" in data) ? data.d : data;
console.log("payload:", payload, "typeof:", typeof payload);


const hasMessage = payload && typeof payload === "object" && typeof payload.Message === "string";
let list = [];
if (Array.isArray(payload)) {
    list = payload;
} else if (payload && typeof payload === "object") {
    if (Array.isArray(payload.data)) list = payload.data;
    else if (Array.isArray(payload.result)) list = payload.result;
    else if (Array.isArray(payload.items)) list = payload.items;
}

console.log("hasMessage:", hasMessage, "list length:", list.length);

           if (!hasMessage && list.length > 0) {

//ea vishal return profile issue changes
       
                $("#noReturnProfileData").hide();
                $("#stockwatchtable").show();


                //$(".mobileWatch").hide();
                //var splitData = data.d.split("\n");
                //$("#returnprofiledate1").html("Index Value as of " + splitData[0]);

                /* var returnsData = JSON.parse(splitData[1]);*/
                var returnsData = data;
                //var p = "string" == typeof data.d ? eval("(" + data.d + ")") : data.d,
                var broserWidth = $(window).width();
                var mobileViewHtml = "";
                $("#mobilewatchTable").show();
                $("#stockwatchtable tbody tr").remove(), $("#mobilewatchTable").html("");
                if (broserWidth > 991) {
                    $("#stockwatchtable thead tr").show();
                } else {
                    $("#stockwatchtable thead tr").hide();
                }
                for (var i = 0; i < returnsData.length; i++)
                    broserWidth > 991
                        ? $("#stockwatchtable").append(
                            "<tr><td data-th='Symbol'>" +
                            returnsData[i].INDEX_NAME +
                            "</td><td data-th='1M'>" +
                            returnsData[i].RET_ONEMONTH +
                            "</td><td data-th='3M'>" +
                            returnsData[i].RET_THREEMONTH +
                            "</td><td data-th='1Yr'>" +
                            returnsData[i].RET_ONEYEAR +
                            "</td><td data-th='3Yr'>" +
                            returnsData[i].RET_THREEYEAR +
                            "</td><td data-th='5Yr'>" +
                            returnsData[i].RET_FIVEYEAR +
                            "</td><td data-th='10yr'>" +
                            returnsData[i].RET_TENYEAR +
                            "</td>"
                        )
                        : ((mobileViewHtml += '<div class="fundBlock">'),
                            (mobileViewHtml += '<ul class="fundBlockIn">'),
                            (mobileViewHtml += "<li>"),
                            (mobileViewHtml += "<span>" + returnsData[i].INDEX_NAME + "</span>"),
                            (mobileViewHtml += "<label>Symbol</label></li>"),
                            (mobileViewHtml += "<li>"),
                            (mobileViewHtml += "<span>" + returnsData[i].RET_ONEMONTH + "</span>"),
                            (mobileViewHtml += "<label>1M</label></li>"),
                            (mobileViewHtml += "<li>"),
                            (mobileViewHtml += "<span>" + returnsData[i].RET_THREEMONTH + "</span>"),
                            (mobileViewHtml += "<label>3M</label></li>"),
                            (mobileViewHtml += "</ul>"),
                            (mobileViewHtml += '<ul id="rel2" class="fundBlockIn">'),
                            (mobileViewHtml += "<li>"),
                            (mobileViewHtml += "<span>" + returnsData[i].RET_ONEYEAR + "</span>"),
                            (mobileViewHtml += "<label>1Yr</label></li>"),
                            (mobileViewHtml += "<li>"),
                            (mobileViewHtml += "<span>" + returnsData[i].RET_THREEYEAR + "</span>"),
                            (mobileViewHtml += "<label>3Yr</label></li>"),
                            (mobileViewHtml += "<li>"),
                            (mobileViewHtml += "<span>" + returnsData[i].RET_FIVEYEAR + "</span>"),
                            (mobileViewHtml += "<label>5Yr</label></li>"),
                            (mobileViewHtml += "</ul>"),
                            (mobileViewHtml += '<ul class="fundBlockIn">'),
                            (mobileViewHtml += "<li>"),
                            (mobileViewHtml += "<span>" + returnsData[i].RET_TENYEAR + "</span>"),
                            (mobileViewHtml += "<label>10Yr</label></li></ul>"),
                            (mobileViewHtml += "</div>"));
                $("#mobilewatchTable").html(mobileViewHtml);

                //for (var i = 0; i < p.length; i++) broserWidth > 991 ? $("#stockwatchtable").append("<tr><td data-th='Symbol'>" + p[i].INDEX_NAME + "</td><td data-th='1M'>" + p[i].RET_ONEMONTH + "</td><td data-th='3M'>" + p[i].RET_THREEMONTH + "</td><td data-th='1Yr'>" + p[i].RET_ONEYEAR + "</td><td data-th='3Yr'>" + p[i].RET_THREEYEAR + "</td><td data-th='5Yr'>" + p[i].RET_FIVEYEAR + "</td><td data-th='10yr'>" + p[i].RET_TENYEAR + "</td>") : (mobileViewHtml += '<div class="fundBlock">', mobileViewHtml += '<ul class="fundBlockIn">', mobileViewHtml += "<li>", mobileViewHtml += "<span>" + p[i].INDEX_NAME + "</span>", mobileViewHtml += "<label>Symbol</label></li>", mobileViewHtml += "<li>", mobileViewHtml += "<span>" + p[i].RET_ONEMONTH + "</span>", mobileViewHtml += "<label>1M</label></li>", mobileViewHtml += "<li>", mobileViewHtml += "<span>" + p[i].RET_THREEMONTH + "</span>", mobileViewHtml += "<label>3M</label></li>", mobileViewHtml += "</ul>", mobileViewHtml += '<ul id="rel2" class="fundBlockIn">', mobileViewHtml += "<li>", mobileViewHtml += "<span>" + p[i].RET_ONEYEAR + "</span>", mobileViewHtml += "<label>1Yr</label></li>", mobileViewHtml += "<li>", mobileViewHtml += "<span>" + p[i].RET_THREEYEAR + "</span>", mobileViewHtml += "<label>3Yr</label></li>", mobileViewHtml += "<li>", mobileViewHtml += "<span>" + p[i].RET_FIVEYEAR + "</span>", mobileViewHtml += "<label>5Yr</label></li>", mobileViewHtml += "</ul>", mobileViewHtml += '<ul class="fundBlockIn">', mobileViewHtml += "<li>", mobileViewHtml += "<span>" + p[i].RET_TENYEAR + "</span>", mobileViewHtml += "<label>10Yr</label></li></ul>", mobileViewHtml += "</div>");
            } else {
                var broserWidth = $(window).width();
                $("#returnprofiledate1").html("");
                var dateTrading1 = $("#datepickerReturnProfile").datepicker("getDate") || new Date();
                var noTradingdate = $.datepicker.formatDate('dd M, yy', dateTrading1)
                $("#userSelectedDate").html(noTradingdate);
                if (broserWidth > 991) {
                    $("#stockwatchtable").hide();
                    $("#noReturnProfileData").show();
                } else {
                    $("#stockwatchtable").hide();
                    $("#mobilewatchTable").hide();
                    $("#noReturnProfileData").show();
                }
            }
            loaderhide();
        },
        //error: function (a) {
        //    console.log("Error: " + error);
        //    console.log("Status: " + status);
        //    console.log(xhr);
        //    alert("An error occurred. Please try again later.");
        //    console.log(a);

        error: function (xhr, status, error) {
            console.log("Error: " + error);  // Now 'error' is defined
            console.log("Status: " + status);
            console.log(xhr);
            alert("An error occurred. Please try again later.");

        },
    });
}


var RecentDate = "";
function getRecentDateReturnProfile(table) {
    //var jsonData = "{'name':'" + iname + "','startDate':'" + startDate + "','endDate':'" + endDate + "','historicaltype' :'" + historicaltype + "'}";
    // var jsonData = "{'name':'" + table + "'}";
    var jsonData = '{"name":"' + table + '"}';

    var sendjson = {};
    sendjson.cinfo = jsonData;
    $.ajax({
        type: "POST",
        url: "/BackPage/GetRecentDate",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        async: false,
        data: JSON.stringify({ cinfo: JSON.stringify({ name: table }) }), // Wrap cinfo properly
        success: function (result) {
            console.log("AJAX Success:", result);
            if (result.error) {
                console.error("Server Error:", result.error);
            } else {
                RecentDate = result.date;
            }
        },
        error: function (xhr, status, error) {
            console.error("AJAX Error:", status, error, xhr.responseText);
        }
    });

    return false;
}

//function curDate() {

//    var b = $(".btn-select-table").text();
//    getRecentDateReturnProfile(b);
//    //var today = new Date;
//    //today.setDate(today.getDate() - 1);
//    //var dd = today.getDate();
//    //var mm = today.getMonth() + 1;//January is 0!
//    //var yyyy = today.getFullYear();
//    //if (dd < 10) { dd = "0" + dd }
//    //if (mm < 10) { mm = "0" + mm }
//    var ActualDate = RecentDate.split("/");
//    var dd = ActualDate[1];
//    var mm = ActualDate[0];
//    var yyyy = ActualDate[2];
//    ActualDate = dd + "/" + mm + "/" + yyyy;
//    $(".range-date-picker").val(ActualDate)
//}




const today = new Date().toLocaleDateString('en-GB').split('/').join('');



var historicalindex = null,
    PePbDivYieldindex = null,
    TotalReturnindex = null,
    sdate = today,
    edate = today,
    indicesresult = null,
    trchartid = null,
    globaldata = "",
    Sessionglobaldata = "",
    indexname = "",
    ETFindex = 0,
    selval = "",
    strloc_mapname = "",
    minNews = 15;
$("ul.nav-pills li a").click(function () {
    var a = $(this).attr("href");
    "#home-2" == a
        ? (window.location.href = "/indices/equity/broad-based-indices")
        : "#settings-10" == a
            ? (window.location.href = "/indices/fixed-income/fixed-income-aggregate-index-series")
            : "#settings-11" == a
                ? (window.location.href = "/indices/fixed-income/target-maturity-index")
                : "#settings-12" == a
                    ? (window.location.href = "/indices/fixed-income/prc-indices")
                    : "#settings-13" == a
                        ? (window.location.href = "/indices/fixed-income/municipal-bond-indices")
                        : "#settings-14" == a
                            ? (window.location.href = "/indices/fixed-income/sovereign-green-bond-indices")
                            : "#settings-16" == a
                                ? (window.location.href = "/indices/multi-asset/multi-asset-indices")
                                : "#settings-6" == a
                                    ? (window.location.href = "/indices/fixed-income/sdl-indices")
                                    : "#settings-9" == a
                                        ? (window.location.href = "/indices/multi-asset/hybrid-indices")
                                        : "#profile-2" == a
                                            ? (window.location.href = "/indices/equity/sectoral-indices")
                                            : "#messages-2" == a
                                                ? (window.location.href = "/indices/equity/thematic-indices")
                                                : "#settings-5" == a
                                                    ? (window.location.href = "/indices/fixed-income/money-market-indices")
                                                    : "#settings-4" == a
                                                        ? (window.location.href = "/indices/fixed-income/corporate-bond-indices/")
                                                        : "#settings-3" == a
                                                            ? (window.location.href = "/indices/fixed-income/gsec-indices")
                                                            : "#settings-2" == a && (window.location.href = "/indices/equity/strategy-indices");
}),
    $(".sortArrow").click(function () {
        loadmoresortele = $(this);
        var a = $(this).closest("th"),
            b = a.index(),
            c = a.closest("table"),
            d = c.find("tbody > tr:visible").get();
        return (
            $(".sortArrow").removeClass("asending"),
            $(".sortArrow").removeClass("desending"),
            $(this).hasClass("desc")
                ? ($(this).removeClass("desc"),
                    $(this).addClass("asending"),
                    $(this).removeClass("desending"),
                    d.sort(function (a, c) {
                        if ("table-row" == $(d).css("display")) {
                            var e = $(a).children("td").eq(b).text().toUpperCase(),
                                f = $(c).children("td").eq(b).text().toUpperCase();
                            return b <= 1 ? Ascending(e, f) : Ascendingnum(e, f);
                        }
                    }))
                : ($(this).addClass("desc"),
                    $(this).removeClass("asending"),
                    $(this).addClass("desending"),
                    d.sort(function (a, c) {
                        if ("table-row" == $(d).css("display")) {
                            var e = $(a).children("td").eq(b).text().toUpperCase(),
                                f = $(c).children("td").eq(b).text().toUpperCase();
                            return b <= 1 ? Descending(e, f) : Descendingnum(e, f);
                        }
                    })),
            $.each(d, function (a, b) {
                c.children("tbody").append(b);
            }),
            !1
        );
    }),

    $(document).ready(function () {
		$("#settings-11 .bharatWrapp").click(function () { $('.niftyBox').show(); });
        $("#ddlStocksGainers li").click(function () {
            $(".overlay").show();
            var a = $(this).text(),
                b = $.trim(a);
            stockindexwatchfile(b), stockwatchGainersLosersfile(b);
        }),
            $("#ddlStocks li").click(function () {
                $(".overlay").show();
                var a = $(this).text(),
                    b = $.trim(a),
                    asynflag = !0;
                stockindexwatchfile(b), stockwatchfile(b, asynflag);
            }),
            $("#ddlIndexs li").click(function () {
                loadershow(), (asynflag = !0), readLiveIndexFile($(this).text(), asynflag);
            }),
            loaderhide();
            tpanetabSectionjs();
    }),
    $(document).ready(function () {
       /* importResearchPapers();*/
        $("#ddlHistorical li").click(function () {
            (historicalindex = $(this).text()), $("#selectedin").text(historicalindex);
        }),
            $("#submit_button").click(function () {
                historicalindex = $("#ddlHistoricaltypeeindex").val();
                var b = $("#datepickerFrom").datepicker("getDate") || new Date(),
                    //if (!b) {
                    //    b = new Date();  // If no date is selected, set to the current date
                    //}

                    c = $.datepicker.formatDate("dd-M-yy", b),
                    d = $("#datepickerTo").datepicker("getDate") || new Date(),
                    //if (!d) {
                    //    d = new Date();  // If no date is selected, set to the current date
                    //}

                    e = $.datepicker.formatDate("dd-M-yy", d),
                    f = Date.parse(c),
                    g = Date.parse(e),
                    h = Math.floor((g - f) / 864e5);
                if (b != null) {
                    sdate = $.datepicker.formatDate("ddmmyy", b);
                }
                if (d != null) {
                    edate = $.datepicker.formatDate("ddmmyy", d);
                }




                //if (((historicalindex = $("#ddlHistoricaltypeeindex").val()), "" == c && ((c = new Date()), (c = c.format("dd-MMM-yyyy"))), "" == e && ((e = new Date()), (e = e.format("dd-MMM-yyyy"))), "" != c && "" != e && "" != historicalindex))
                //    return f > g ? (alert("Start date cannot be greater than end date"), !1) : (HistoricalData(historicalindex, c, e), !0);

                if (((historicalindex = $("#ddlHistoricaltypeeindex").val()), "" == c && ((c = new Date()), (c = c.toLocaleDateString("en-GB"))), "" == e && ((e = new Date()), (e = e.toLocaleDateString("en-GB"))), "" != c && "" != e && "" != historicalindex))
                    return f > g ? (alert("Start date cannot be greater than end date"), !1) : (HistoricalData(historicalindex, c, e), !0);


            });
    }),
    $(document).ready(function () {
        $("#submit_buttonvixdata").click(function () {
            var b = $("#datepickerFromvixdata").datepicker("getDate"),
                c = $.datepicker.formatDate("dd-M-yy", b),
                d = $("#datepickerTovixdata").datepicker("getDate"),
                e = $.datepicker.formatDate("dd-M-yy", d),
                f = Date.parse(c),
                g = Date.parse(e),
                h = Math.floor((g - f) / 864e5);
            if (b != null) {
                sdate = $.datepicker.formatDate("ddmmyy", b);
            }
            if (d != null) {
                edate = $.datepicker.formatDate("ddmmyy", d);
            }
            if (("" == c && ((c = new Date()), (c = c.format("dd-M-yy"))), "" == e && ((e = new Date()), (e = e.format("dd-M-yy"))), "" != c && "" != e))
                return f > g ? (alert("Start date cannot be greater than end date"), !1) : h > 365 ? (alert("Please select date range not more than 365 days"), !1) : (HistoricalIndiavixData("India Vix", c, e), !0);
        });
    }),
    $(document).ready(function () {
        (PePbDivYieldindex = null), // May15,2024
            $("#pe,#pb,#yield,#all").prop("checked", !0),
            $("#ddlHistoricalDivYield li").click(function () {
                (PePbDivYieldindex = $(this).text()), $("#selecteddivindex").text(PePbDivYieldindex);
            }),
            $("#pb").on("click", function () {
                $("#all").attr("checked", !1), $(this).is(":checked", !0) ? $(".thpb").show() : $(".thpb").hide();
            }),
            $("#yield").on("click", function () {
                $("#all").attr("checked", !1), $(this).is(":checked", !0) ? $(".thdiv").show() : $(".thdiv").hide();
            }),
            $("#pe").on("click", function () {
                $("#all").attr("checked", !1), $(this).is(":checked", !0) ? $(".thpe").show() : $(".thpe").hide();
            }),
            $("#all").on("click", function () {
                $(this).is(":checked", !0)
                    ? ($("#pe,#pb,#yield").prop("checked", !0), $(".thpe").show(), $(".thdiv").show(), $(".thpb").show())
                    : ($("#pe").prop("checked", !1), $("#yield").prop("checked", !1), $("#pb").prop("checked", !1));
            }),
            $(".iislCheck").change(function () {
                $(".iislCheck:checked").length == $(".iislCheck").length && $("#all").prop("checked", !0);
            }),
            $("#submit_buttonDivdata").click(function () {
                PePbDivYieldindex = $("#ddlHistoricaldivtypeeindex").val();
                var a = $("#datepickerFromDivYield").datepicker("getDate") || new Date(),
                    b = $.datepicker.formatDate("dd-M-yy", a),
                    c = $("#datepickerToDivYield").datepicker("getDate") || new Date(),
                    d = $.datepicker.formatDate("dd-M-yy", c),
                    e = Date.parse(b),
                    f = Date.parse(d),
                    g = Math.floor((f - e) / 864e5);
                // For file name
                if (a != null) {
                    sdate = $.datepicker.formatDate("ddmmyy", a);
                }
                if (c != null) {
                    edate = $.datepicker.formatDate("ddmmyy", c);
                }


                //function formatDate(date) {
                //    const day = String(date.getDate()).padStart(2, '0');
                //    const month = date.toLocaleString('default', { month: 'short' });
                //    const year = date.getFullYear();
                //    return `${day}-${month}-${year}`;
                //}

                //b = formatDate(new Date());

                //if (((PePbDivYieldindex = $("#ddlHistoricaldivtypeeindex").val()), "" == c && ((c = new Date()), (c = c.toLocaleDateString("en-GB"))), "" == e && ((e = new Date()), (e = e.toLocaleDateString("en-GB"))), "" != c && "" != e && "" != PePbDivYieldindex))
                //    return e > f ? (alert("Start date cannot be greater than end date"), !1) : (Historicaldivyield(PePbDivYieldindex, b, d), !0);



                return (
                    (PePbDivYieldindex = $("#ddlHistoricaldivtypeeindex").val()),
                    $('.chkboxHolder input[type="checkbox"]').is(":checked")
                        ? ("" == b && ((b = new Date()), (b = b.toLocaleDateString("en-GB"))),
                            "" == d && ((d = new Date()), (d = d.toLocaleDateString("en-GB"))),
                            "" != b && "" != d && ($("#pe").is(":checked", !0) || $("#pb").is(":checked", !0) || $("#yield").is(":checked", !0))
                                ? e > f
                                    ? (alert("Start date cannot be greater than end date"), !1)
                                    : (Historicaldivyield(PePbDivYieldindex, b, d), !0)
                                : void 0)
                        : (alert("Please check at least one index Type."), !1)
                );

                //return (
                //    (PePbDivYieldindex = $("#ddlHistoricaldivtypeeindex").val()),
                //    $('.chkboxHolder input[type="checkbox"]').is(":checked")
                //        ? ("" == b && ((b = new Date()), (b = formatDate(b))),
                //            "" == d && ((d = new Date()), (d = formatDate(d))),
                //            "" != b && "" != d && ($("#pe").is(":checked", !0) || $("#pb").is(":checked", !0) || $("#yield").is(":checked", !0))
                //                ? e > f
                //                    ? (alert("Start date cannot be greater than end date"), !1)
                //                    : (Historicaldivyield(PePbDivYieldindex, b, d), !0)
                //                : void 0)
                //        : (alert("Please check at least one index Type."), !1)
                //);

                console.log('executed')
            });
    }),
    $(document).ready(function () {
        (TotalReturnindex = null),
            $("#ddlHistoricaltotalindex li").click(function () {
                (TotalReturnindex = $(this).text()), $("#selectedTotalindex").text(TotalReturnindex);
            }),
            $("#submit_totalindexhistorical").click(function () {
                TotalReturnindex = $("#ddlHistoricalreturntypeeindex").val();
                var a = $("#datepickerFromtotalindex").datepicker("getDate") || new Date(),
                    b = $.datepicker.formatDate("dd-M-yy", a),
                    c = $("#datepickerTototalindex").datepicker("getDate") || new Date(),
                    d = $.datepicker.formatDate("dd-M-yy", c),
                    e = Date.parse(b),
                    f = Date.parse(d);
                // For file name
                if (a != null) {
                    sdate = $.datepicker.formatDate("ddmmyy", a);
                }
                if (c != null) {
                    edate = $.datepicker.formatDate("ddmmyy", c);
                }
                TotalReturnindex = $("#ddlHistoricalreturntypeeindex").val();
                var g = Math.floor((f - e) / 864e5);

                //if (((historicalindex = $("#ddlHistoricaltypeeindex").val()), "" == c && ((c = new Date()), (c = c.toLocaleDateString("en-GB"))), "" == e && ((e = new Date()), (e = e.toLocaleDateString("en-GB"))), "" != c && "" != e && "" != historicalindex))
                //    return e > f ? (alert("Start date cannot be greater than end date"), !1) : (TotalReturnindexHistoricalData(TotalReturnindex, b, d), !0);



                if (("" == b && ((b = new Date()), (b = b.toLocaleDateString("en-GB"))), "" == d && ((d = new Date()), (d = d.toLocaleDateString("en-GB"))), "" != b && "" != d))
                    return e > f ? (alert("Start date cannot be greater than end date"), !1) : (TotalReturnindexHistoricalData(TotalReturnindex, b, d), !0);

            });
    }),
    $(document).ready(function () {
        $("#Historicalvixdata").hide(), $("#TotalReturnindexvalue").hide(), $("#Divyieldvalue").hide(), $("#ArchivesDailyReport").hide();
        var a = function (b) {
            var e,
                f,
                c = decodeURIComponent(window.location.search.substring(1)),
                d = c.split("&");
            for (f = 0; f < d.length; f++) if (((e = d[f].split("=")), e[0] === b)) return void 0 === e[1] || e[1];
        },
            b = a("option1");
        a("option2"), a("option3");




        b == $(".form3").text() &&
            ($("#HistoricalMenu").text(b), $("#ArchivesDailyReport").show(), $("#show").show(), $("#HistoricalData").hide(), $("#Historicalvixdata").hide(), $("#TotalReturnindexvalue").hide(), $("#Divyieldvalue").hide()),
            $("#maindd li").click(function () {
                $(this).hasClass("form1")
                    ? ($("#HistoricalData").show(),
                        $("#ArchiveDailyReport").prop("selectedIndex", 0),
                        $("#Historicalnodata").show(),
                        $("#nodatafound").hide(),
                        $("#history").hide(),
                        $("#HistoryExport").hide(),
                        $("#Indexname").hide(),
                        $("#pagehistoricaldata").hide(),
                        $("#exporthistorical").hide(),
                        $(".downloads").hide(),
                        $("#Historicalvixdata").hide(),
                        $("#Divyieldvalue").hide(),
                        $("#TotalReturnindexvalue").hide(),
                        $("#ArchivesDailyReport").hide())
                    : $(this).hasClass("form2")
                        ? ($("#Historicalvixdata").show(), $("#ArchiveDailyReport").prop("selectedIndex", 0), $("#HistoricalData").hide(), $("#Divyieldvalue").hide(), $("#TotalReturnindexvalue").hide(), $("#ArchivesDailyReport").hide())
                        : $(this).hasClass("form3")
                            ? ($("#ArchivesDailyReport").show(),
                                $("#Indexdailyname").hide(),
                                $("#show").show(),
                                $("#tblreport").hide(),
                                $("#HistoricalData").hide(),
                                $("#Historicalvixdata").hide(),
                                $("#TotalReturnindexvalue").hide(),
                                $("#Divyieldvalue").hide())
                            : $(this).hasClass("form4")
                                ? ($("#Divyieldvalue").show(),
                                    $("#Historicaldivnodata").show(),
                                    $("#ArchiveDailyReport").prop("selectedIndex", 0),
                                    $("#historydivyieldexport").hide(),
                                    $("#exporthistoricaldiv").hide(),
                                    $(".downloads").hide(),
                                    $("#pagehistoricalpepbdata").hide(),
                                    $("#noDivdatafound").hide(),
                                    $("#Indexdivname").hide(),
                                    $("#historydivyield").hide(),
                                    $("#historytotalindexexport").hide(),
                                    $("#HistoricalData").hide(),
                                    $("#Historicalvixdata").hide(),
                                    $("#TotalReturnindexvalue").hide(),
                                    $("#ArchivesDailyReport").hide())
                                : $(this).hasClass("form5") &&
                                ($("#TotalReturnindexvalue").show(),
                                    $("#TotalReturnnodatafound").hide(),
                                    $("#historytotalindex").hide(),
                                    $("#pagehistoricalTotalreturndata").hide(),
                                    $("#IndexTotalname").hide(),
                                    $(".downloads").hide(),
                                    $("#exportTotalindex").hide(),
                                    $("#historytotalindexexport").hide(),
                                    $("#TotalReturnnodata").show(),
                                    $("#HistoricalData").hide(),
                                    $("#Divyieldvalue").hide(),
                                    $("#Historicalvixdata").hide(),
                                    $("#ArchivesDailyReport").hide());
            }),
            loaderhide();
    });
var incIndex = 15;
$("#exporthistorical").on("click", function (a) {
    exportTableToCSV.call(this, $("#HistoryExport"), historicalindex + "_Historical_PR_" + sdate + "to" + edate + ".csv");
}),
    $("#exporthistoricalvix").on("click", function (a) {
        exportTableToCSV.call(this, $("#historyvixdata"), "HistoricalVix_Data.csv");
    }),
    $("#exportTotalindex").on("click", function (a) {
        exportTableToCSV.call(this, $("#historytotalindexexport"), TotalReturnindex + "_Historical_TR_" + sdate + "to" + edate + ".csv");
    }),
    $("#exporthistoricaldiv").on("click", function (a) {
        exportTableToCSV.call(this, $("#historydivyieldexport"), PePbDivYieldindex + "_Historical_PE_PB_DIV_Data_" + sdate + "to" + edate + ".csv");
    }),
    $(function () {
        $("#chkAccept").on("click", function () {
            $("#chkAccept:input:checked").length > 0 ? $("#pdfLink").show() : $("#pdfLink").hide();
        });
    }),
    $("#ddlIndices li").click(function () {
        var a = $(this).attr("rel");
        window.location.href = a;
    }),
    $("#heatMapDetail a").click(function () {
        var a = $("#selectedin").text();
        window.location.href = "/market-data/heat-map-detail?Indexname=" + a;
    }),
    $(document).ready(function () {

        /return-profile/.test(window.location.href) && getIndex();
    }),
    $(document).ready(function () {
        $(".sfsearchSubmit").wrap('<span class="sfsearchSubWrap"></span>'),
            $("input.sfsearchTxt").wrap('<span class="sfsearchTxt"></span>'),
            $(".sfsearchSubmit").val(""),
            $("input.sfsearchTxt").attr("placeholder", "What are you looking for?");
    }),
    $(document).on("click", ".sfsearchSubWrap", function (a) {
        a.stopPropagation(),
            $(window).width() > 767
                ? ($(".searchWrap").toggleClass("width100"), $("input.sfsearchTxt").css("width", "100%"), $(".sfsearchSubWrap,.sfsearchSubWrap:after").toggle(), $(".sfsearchTxt").fadeIn())
                : ($(".searchWrap").toggleClass("width100"), $(".sfsearchTxt").toggle()),
            $("input.sfsearchTxt").focus();
    }),
    $(document).on("click", ".sfsearchTxt", function (a) {
        a.stopPropagation();
    }),
    $(document).click(function () {
        $(".searchWrap").removeClass("width100"), $(".sfsearchTxt").fadeOut(), $(".sfsearchSubWrap").fadeIn();
    });
function SortArray(obj) {
    var a = $(obj).closest("th"),
        b = a.index(),
        c = a.closest("table"),
        d = c.find("tbody > tr:visible").get();
    $(obj).hasClass("asending")
        ? ($(obj).removeClass("desc"),
            $(obj).addClass("asending"),
            $(obj).removeClass("desending"),
            d.sort(function (a, c) {
                if ("table-row" == $(d).css("display")) {
                    var e = $(a).children("td").eq(b).text().toUpperCase(),
                        f = $(c).children("td").eq(b).text().toUpperCase();
                    return b <= 1 ? Ascending(e, f) : Ascendingnum(e, f);
                }
            }))
        : ($(obj).addClass("desc"),
            $(obj).removeClass("asending"),
            $(obj).addClass("desending"),
            d.sort(function (a, c) {
                if ("table-row" == $(d).css("display")) {
                    var e = $(a).children("td").eq(b).text().toUpperCase(),
                        f = $(c).children("td").eq(b).text().toUpperCase();
                    return b <= 1 ? Descending(e, f) : Descendingnum(e, f);
                }
            })),
        $.each(d, function (a, b) {
            c.children("tbody").append(b);
        }),
        !1;
}

$("#exportHeatmapDetail").on("click", function (a) {
    // index movers heatmap detail page.
    exportTableToCSV.call(this, $("#stockHeatmaptable"), "HeatmapDetail_Data.csv");
});

$("#exportreturnprofile").on("click", function (a) {
    // Return profile Data
    exportTableToCSV.call(this, $("#stockwatchtable"), "Returnprofile_Data.csv");
});
var incrmntCounter = 50;
var newCounter = "";
$("#loadmorestock").on("click", function () {
    // Return profile Data
    loadershow();
    $("#loadmorestock").show();
    a = JSON.parse(sessionStorage.Sessionglobaldata);
    newCounter = a.data.length;
    for ($("#indexvalue").html(a.latestData[0].ltp), $("#indexgreenpercentage").html(a.latestData[0].ch), $("#indexgreenvalue").html(a.latestData[0].per), generatID = 1, i = counter; i < counter + incrmntCounter; i++) {
        (nifty50 = a.data[i].ltP),
            (nifty50 = nifty50.replace(/\,/g, "")),
            (nifty50 = parseFloat(nifty50)),
            (nifty50close = a.data[i].previousClose),
            (nifty50close = nifty50close.replace(/\,/g, "")),
            (nifty50close = parseFloat(nifty50close)),
            //(Change = nifty50 - nifty50close),
            (Change = a.data[i].ptsC),
            (Change = Change.replace(/\,/g, "")),
            (Change = parseFloat(Change)),
            (PerChange = (Change / nifty50close) * 100);
        var c = $(window).width();
        if (c > 991)
            $("#stockwatchtable").append(
                "<tr><td>" +
                a.data[i].symbol +
                "</td><td><span id='perchangedesk" +
                i +
                "' class='shareDown'>" +
                a.data[i].per +
                "%</span></td><td><span id='changedesk" +
                i +
                "' class='red'>" +
                Change.toFixed(2) +
                "</span></td><td>" +
                a.data[i].low +
                "<div class='rel' id='low" +
                i +
                "'></div></td><td>" +
                a.data[i].ltP +
                "</td><td>" +
                a.data[i].high +
                "</td><td>" +
                a.data[i].previousClose +
                "</td><td>" +
                a.data[i].open +
                "</td><td>" +
                a.data[i].trdVolM +
                "</td><td>" +
                a.data[i].mVal +
                "</td><td>" +
                a.data[i].wklo +
                "</td><td>" +
                a.data[i].wkhi +
                "</td> </tr>"
            ),
                doSlide(),
                a.data[i].per > 0 ? ($("#perchangedesk" + i).removeClass("shareDown"), $("#perchangedesk" + i).addClass("shareUp")) : ($("#perchangedesk" + i).removeClass("shareUp"), $("#perchangedesk" + i).addClass("shareDown")),
                Change > 0 ? ($("#changedesk" + i).removeClass("red"), $("#changedesk" + i).addClass("green")) : ($("#changedesk" + i).removeClass("green"), $("#changedesk" + i).addClass("red"));
        else {
            var d = "";
            (d += '<div class="fundBlock">'),
                (d += '<ul class="fundBlockIn">'),
                (d += "<li>"),
                (d += "<span>" + a.data[i].symbol + "</span>"),
                (d += "<label>Symbol</label></li>"),
                // (d += "<li>"),
                // (d += '<span class="smallchart" id="areacontainer' + generatID + '" style="height: 50px; width:80px; margin: 0 auto"></span>'),
                // (d += "<label>Today</label>"),
                // (d += "</li>"),
                (d += "<li>"),
                (d += '<span id="perchange' + i + '" class="shareUp">' + a.data[i].per + "%</span>"),
                (d += "<label>%Chng</label></li>"),
                (d += "</ul>"),
                (d += '<ul id="rel2' + i + '" class="fundBlockIn stockBar">'),
                (d += "<li><span>" + a.data[i].low + "</span><label>Day Low</label></li>"),
                (d += '<li><span class="green">' + a.data[i].ltP + "</span>"),
                (d += "<label>LTP</label></li>"),
                (d += "<li><span>" + a.data[i].high + "</span>"),
                (d += "<label>Day HIGH</label></li></ul>"),
                (d += '<ul class="fundBlockIn">'),
                (d += "<li><span>" + a.data[i].previousClose + "</span>"),
                (d += "<label>Prev Close</label></li>"),
                (d += "<li><span>" + a.data[i].open + "</span><label>Day Open</label> </li>"),
                (d += "<li><span>" + Change.toFixed(2) + "</span><label>chng</label></li></ul>"),
                (d += '<ul class="fundBlockIn">'),
                (d += "<li><span>" + a.data[i].wklo + "</span><label>52w LOW</label></li>"),
                (d += "<li><span>" + a.data[i].wkhi + "</span><label>52w High</label></li></ul>"),
                (d += '<ul class="fundBlockIn">'),
                (d += "<li><span>" + a.data[i].trdVolM + "</span>"),
                (d += "<label>Vol (Lacs)</label></li>"),
                (d += "<li><span>" + a.data[i].mVal + "</span><label>(Crores) Turnover</label></li></ul>"),
                (d += "</div>"),
                $("#mobilewatch").append(d);
            doSlide_mob("rel2" + i), a.data[i].per > 0 ? ($("#perchange" + i).removeClass("shareDown"), $("#perchange" + i).addClass("shareUp")) : ($("#perchange" + i).removeClass("shareUp"), $("#perchange" + i).addClass("shareDown"));
        }
        generatID += 1;
    }
    counter = counter + incrmntCounter;
    if (c > 991) {
        var h = $("#stockwatchtable tbody tr").length;
        if (minNews + 15 <= h) {
            minNews = minNews + 15;
            d = minNews - 14;
            //minNews = c
            //d=minNews
        } else {
            d = minNews + 1;
            minNews = h;
        }

        //for (h <= minNews && (minNews = h), i = d; i <= minNews; i++) {
        //15May2024
        //for (minNews = h, i = d; i <= h; i++) {
        //    var j = $("#stockwatchtable tbody tr:nth-child(" + i + ")"),
        //        k = j.find("td:nth-child(2)").attr("id"),
        //        l = j.find("td:nth-child(1)").html(),
        //        m = k;
        //    //initCMintraday(m, l);
        //}
    }
    else {
        var c = $(".fundBlock").length;
        //15May2024
        //if (((minNews = minNews + 6 <= c ? minNews + 5 : c), (d = minNews - 4), (a = minNews - 5)))
        //    for (i = d; i <= minNews; i++) {
        //        var j = $("#mobilewatch .fundBlock:nth-child(" + i + ")"),
        //            k = j.find("ul li:nth-child(2) span").attr("id"),
        //            l = j.find("ul li:nth-child(1) span").html(),
        //            m = k;
        //        //initCMintraday(m, l);
        //    }
    }
});
// 31-10-2022  scrollbar changes

(function ($) {
    if ($(window).width() > 767) {
        $(window).on("load", function () {
            $(".mainNav .yamm-fw .dropdown-menu").mCustomScrollbar({
                axis: "y",
                setHeight: 500,
                mouseWheelPixels: 50
            });

            // $(".mainNav .grid-demo .nav-pills").mCustomScrollbar({
            //     axis: "y",
            //     setHeight: 450
            // });
        });
    }
})(jQuery);

// Jan19,2026
$(document).on("click", ".redirectIndexWatch", function (e) {
    e.preventDefault();
    if (confirm("You are about to leave the website of Nifty Indices Limited (Nifty Indices).\nYou have selected a link that will take you away from Nifty Indices. This site may be maintained by an entity other than Nifty Indices or its Group Companies. Nifty Indices is not responsible for the content of the web site you are visiting from the selected link.\nYou are aware and you expressly acknowledge and agree that the linked site may not be under the control of Nifty Indices and Nifty Indices shall not be responsible for the contents of such site or any link contained in such site, or any changes or updates to such web site. Nifty Indices shall not be responsible or liable in any manner whatsoever for any payments that you make for any services that you may avail from such websites or the selected link.\nNifty Indices is not responsible for the accuracy, appropriateness or the reliability of the data or content available on the website you are visiting from the selected link. Unless expressly mentioned, Nifty Indices does not endorse any views, data and/or content available on the selected website.\nOnce you visit the website from the selected link, the policies/ terms/ conditions of such selected websites may be applicable on you.\nThe availability of this link on the Nifty Indices website shall not be construed as advertisement and/ or endorsement of such website by Nifty Indices in any manner whatsoever.\nIf you decide to visit such site, you agree and acknowledge to do so at your own risk, and it is your responsibility to take all protective measures to guard against viruses or any other destructive elements that you may encounter.")) {
        window.open("https://www.nseindia.com/market-data/live-market-indices", "_blank");
    }
    else { }
});

$(document).on("click", ".redirectStockWatch", function (e) {
    e.preventDefault();
    if (confirm("You are about to leave the website of Nifty Indices Limited (Nifty Indices).\nYou have selected a link that will take you away from Nifty Indices. This site may be maintained by an entity other than Nifty Indices or its Group Companies. Nifty Indices is not responsible for the content of the web site you are visiting from the selected link.\nYou are aware and you expressly acknowledge and agree that the linked site may not be under the control of Nifty Indices and Nifty Indices shall not be responsible for the contents of such site or any link contained in such site, or any changes or updates to such web site. Nifty Indices shall not be responsible or liable in any manner whatsoever for any payments that you make for any services that you may avail from such websites or the selected link.\nNifty Indices is not responsible for the accuracy, appropriateness or the reliability of the data or content available on the website you are visiting from the selected link. Unless expressly mentioned, Nifty Indices does not endorse any views, data and/or content available on the selected website.\nOnce you visit the website from the selected link, the policies/ terms/ conditions of such selected websites may be applicable on you.\nThe availability of this link on the Nifty Indices website shall not be construed as advertisement and/ or endorsement of such website by Nifty Indices in any manner whatsoever.\nIf you decide to visit such site, you agree and acknowledge to do so at your own risk, and it is your responsibility to take all protective measures to guard against viruses or any other destructive elements that you may encounter.")) {
        window.open("https://www.nseindia.com/market-data/live-equity-market", "_blank");
    }
    else { }
});

$(document).on("click", ".redirectEtf", function (e) {
    e.preventDefault();
    if (confirm("You are about to leave the website of Nifty Indices Limited (Nifty Indices).\nYou have selected a link that will take you away from Nifty Indices. This site may be maintained by an entity other than Nifty Indices or its Group Companies. Nifty Indices is not responsible for the content of the web site you are visiting from the selected link.\nYou are aware and you expressly acknowledge and agree that the linked site may not be under the control of Nifty Indices and Nifty Indices shall not be responsible for the contents of such site or any link contained in such site, or any changes or updates to such web site. Nifty Indices shall not be responsible or liable in any manner whatsoever for any payments that you make for any services that you may avail from such websites or the selected link.\nNifty Indices is not responsible for the accuracy, appropriateness or the reliability of the data or content available on the website you are visiting from the selected link. Unless expressly mentioned, Nifty Indices does not endorse any views, data and/or content available on the selected website.\nOnce you visit the website from the selected link, the policies/ terms/ conditions of such selected websites may be applicable on you.\nThe availability of this link on the Nifty Indices website shall not be construed as advertisement and/ or endorsement of such website by Nifty Indices in any manner whatsoever.\nIf you decide to visit such site, you agree and acknowledge to do so at your own risk, and it is your responsibility to take all protective measures to guard against viruses or any other destructive elements that you may encounter.")) {
        window.open("https://www.nseindia.com/market-data/exchange-traded-funds-etf", "_blank");
    }
    else { }
});
$(document).on("click", ".redirectIndexMovers", function (e) {
    e.preventDefault();
    if (confirm("You are about to leave the website of Nifty Indices Limited (Nifty Indices).\nYou have selected a link that will take you away from Nifty Indices. This site may be maintained by an entity other than Nifty Indices or its Group Companies. Nifty Indices is not responsible for the content of the web site you are visiting from the selected link.\nYou are aware and you expressly acknowledge and agree that the linked site may not be under the control of Nifty Indices and Nifty Indices shall not be responsible for the contents of such site or any link contained in such site, or any changes or updates to such web site. Nifty Indices shall not be responsible or liable in any manner whatsoever for any payments that you make for any services that you may avail from such websites or the selected link.\nNifty Indices is not responsible for the accuracy, appropriateness or the reliability of the data or content available on the website you are visiting from the selected link. Unless expressly mentioned, Nifty Indices does not endorse any views, data and/or content available on the selected website.\nOnce you visit the website from the selected link, the policies/ terms/ conditions of such selected websites may be applicable on you.\nThe availability of this link on the Nifty Indices website shall not be construed as advertisement and/ or endorsement of such website by Nifty Indices in any manner whatsoever.\nIf you decide to visit such site, you agree and acknowledge to do so at your own risk, and it is your responsibility to take all protective measures to guard against viruses or any other destructive elements that you may encounter.")) {
        window.open("https://www.nseindia.com/index-tracker/NIFTY%2050", "_blank");
    }
    else { }
});
function tpanetabSectionjs() {
    $('ul.tpanetabSection li').click(function (e) {
        e.preventDefault();
        var tab_index = $(this).index();
        console.log(tab_index);

        $(this).parent('ul.tpanetabSection').find(' li').removeClass('current');
        $(this).closest('.tab-pane').find('.navtabContentMain .tbContent').removeClass('current');

        $(this).addClass('current');
        // $("#" + tab_id).addClass('current');
        $(this).closest('.tab-pane').find('.navtabContentMain .tbContent').eq(tab_index).addClass('current');
    })
}