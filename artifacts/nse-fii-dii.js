'use strict';

var tableElement = void 0,
    tableElementNse = void 0;

B.on(document, 'allGood', function () {
    initData();
    initDataNse();
});

function initData() {
    B.get('/json/reports/fii-dii.json').then(function (resp) {
        var respJSONObj = JSON.parse(resp);
        tableElement = customTable({ tableStyle: { id: 'fiidiiTable', class: 'common_table customHeight-table tableScroll' }, colData: respJSONObj.columns || [], rowData: [] });
        B.render(tableElement, B.findOne('#fii-dii-table-container'));
        loadData();
        loadNotes();
        includeJs("/assets/js/deque-patterns.min.js");
    });
}
function initDataNse() {
    B.get('/json/reports/fii-dii.json').then(function (resp) {
        var respJSONObj = JSON.parse(resp);
        tableElementNse = customTable({ tableStyle: { id: 'fiidiiTableNse', class: 'common_table customHeight-table tableScroll' }, colData: respJSONObj.columns || [], rowData: [] });
        B.render(tableElementNse, B.findOne('#fii-dii-nse-table-container'));
        loadDataNse();
        includeJs("/assets/js/deque-patterns.min.js");
    });
}

function loadData() {
    B.get('/api/fiidiiTradeReact').then(function (resp) {
        var respJSON = JSON.parse(resp);
        var records = respJSON;
        tableElement.state.rowData = records || [];
    });
}

function loadDataNse() {
    B.get('/api/fiidiiTradeNse').then(function (resp) {
        var respJSON = JSON.parse(resp);
        var records = respJSON;
        tableElementNse.state.rowData = records || [];
    });
}

function downloadCSV() {
    downloadFile('/api/fiidiiTradeReact?csv=true');
}

function downloadNseCSV() {
    downloadFile('/api/fiidiiTradeNse?csv=true');
}
function includeJs(jsFilePath) {
    var js = document.createElement("script");
    js.type = "text/javascript";
    js.src = jsFilePath;
    //console.log(" document.body", document.body,"js",js)
    document.body.appendChild(js);
    $('.deque-table-sortable-group').each(function () {
        if ($(this).find('.liveRegion').length === 0) {
            $(this).prepend('<span class="liveRegion" aria-live="polite" readCaptions="false" style="color: white;"></span>');
        }
    });
}