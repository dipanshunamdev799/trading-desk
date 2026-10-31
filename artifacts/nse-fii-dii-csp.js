'use strict';

B.on(document, 'allGood', function () {
    var nseBtn = document.getElementById('downloadNseCsvBtn');
    if (nseBtn) {
        nseBtn.addEventListener('click', function (e) {
            e.preventDefault();
            downloadNseCSV();
        });
    }

    var csvBtn = document.getElementById('downloadCsvBtn');
    if (csvBtn) {
        csvBtn.addEventListener('click', function (e) {
            e.preventDefault();
            downloadCSV();
        });
    }
});