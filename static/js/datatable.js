$(document).ready(function() {
    $(".data-table").each(function(_, table) {
        $(table).DataTable();
    });
});

$(document).ready(function() {
    $('#earning-table-view').DataTable({
        // "scrollY": 300,
        "scrollX": true,
        // "paging": true,
        // "responsive": true,
        // "searching": true,
        // "lengthChange": false,
        // "searching": true,
        "ordering": false,
        // "info": true,
        // "autoWidth": false,
        "responsive": false,
    });
});
$(document).ready(function() {
    $('#deposite-view-table').DataTable({
        // "scrollY": 300,
        "scrollX": true,
        // "paging": true,
        // "responsive": true,
        // "searching": true,
        // "lengthChange": false,
        // "searching": true,
        "ordering": false,
        // "info": true,
        // "autoWidth": false,
        "responsive": false,
    });
});
$(document).ready(function() {
    $('#deposite-all-table').DataTable({
        "paging": true,
        "scrollX": true,
        "lengthChange": false,
        "searching": false,
        "ordering": false,
        "info": true,
        "autoWidth": false,
        "responsive": false,
    });
});


$(document).ready(function() {
    $('#expenditure-view-table').DataTable({
        // "scrollY": 300,
        "scrollX": true,
        // "paging": true,
        // "responsive": true,
        // "searching": true,
        // "lengthChange": false,
        // "searching": true,
        "ordering": false,
        // "info": true,
        // "autoWidth": false,
        "responsive": false,
    });
});

$(document).ready(function() {
    $('#meeting-home-table').DataTable({
        // "scrollY": 300,
        "scrollX": true,
        // "paging": true,
        // "responsive": true,
        // "searching": true,
        // "lengthChange": false,
        // "searching": true,
        "ordering": false,
        // "info": true,
        // "autoWidth": false,
        "responsive": false,
    });
});

$(document).ready(function() {
    $('#meeting-agenda').DataTable({
        // "scrollY": 300,
        "scrollX": true,
        // "paging": true,
        // "responsive": true,
        // "searching": true,
        // "lengthChange": false,
        // "searching": true,
        "ordering": false,
        // "info": true,
        // "autoWidth": false,
        "responsive": false,
    });
});

$(document).ready(function() {
    $('#all-member').DataTable({
        "paging": true,
        "scrollX": true,
        "lengthChange": false,
        "searching": false,
        "ordering": false,
        "info": true,
        "autoWidth": false,
        "responsive": false,
    });
});

$(document).ready(function() {
    $('#date_range_deposit_report').DataTable({
        "paging": true,
        "scrollX": true,
        "lengthChange": false,
        "searching": false,
        "ordering": false,
        "info": true,
        "autoWidth": false,
        "responsive": false,
    });
});

$(document).ready(function() {
    $('#member_wise_deposit_report').DataTable({
        "paging": true,
        "scrollX": true,
        "lengthChange": false,
        "searching": false,
        "ordering": false,
        "info": true,
        "autoWidth": false,
        "responsive": false,
    });
});

$(document).ready(function() {
    $('#attend-table').DataTable({
        "paging": true,
        "scrollX": true,
        "lengthChange": false,
        "searching": false,
        "ordering": false,
        "info": true,
        "autoWidth": false,
        "responsive": false,
    });
    $('#agend-table').DataTable({
        "paging": true,
        "scrollX": true,
        "lengthChange": false,
        "searching": false,
        "ordering": false,
        "info": true,
        "autoWidth": false,
        "responsive": false,
    });
});