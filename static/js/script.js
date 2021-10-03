document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#deposit-deny-btn').forEach(function(button) {
        button.onclick = function() {
            $('#deposit-deny-id-container').val($(this).attr("data-id"));
        }
    });
});

$('.deny-deposit').click(function(event) {
    event.preventDefault()
        // var postId = $(this).data("catid")
    var deposit_id = $('#deposit-deny-id-container').val()
    console.log(deposit_id)
    $.ajax({
        type: "POST",
        url: `deposit/deny/${deposit_id}`,
        data: {
            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
            deposit_id: deposit_id
        },
        success: function(data1) {

            if (data1.status == "error") {
                // alert(data1.message)
                $('#deposit-deny').modal('hide')
                $(`.approve-deny-${deposit_id}`).html("")
                toastr.error(data1.message);
            } else if (data1.status == "success") {
                //alert(data1.message)
                $('#deposit-deny').modal('hide')
                $(`.approve-deny-${deposit_id}`).html("")
                    // select = document.getElementById('#os_type_dd');

                toastr.success(data1.message);
            }
        }
    })
})


document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#deposit-approve-btn').forEach(function(button) {
        button.onclick = function() {
            $('#deposit-approve-id-container').val($(this).attr("data-id"));
        }
    });
});

$('.approve-deposit').click(function(event) {
    event.preventDefault()
        // var postId = $(this).data("catid")
    var deposit_id = $('#deposit-approve-id-container').val()
    console.log(deposit_id)
    $.ajax({
        type: "POST",
        url: `deposit/approve/${deposit_id}`,

        data: {
            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
            deposit_id: deposit_id
        },
        beforeSend: function() {
            $("#deposit-buttons").hide();
            $("#deposit-loader").show();
        },
        complete: function() {
            // $("#deposit-buttons").show();
            $("#deposit-loader").hide();
        },
        success: function(data1) {

            if (data1.status == "error") {
                // alert(data1.message)
                $('#deposit-approve').modal('hide')
                    // $(`.approve-deny-${deposit_id}`).html("")

                toastr.error(data1.message);
            } else if (data1.status == "success") {
                //alert(data1.message)
                $('#deposit-approve').modal('hide')
                $(`.approve-deny-${deposit_id}`).html("")
                $(`.deposit-status-${deposit_id}`).html("<span class='badge bg-success'>Approved</span>")
                    // select = document.getElementById('#os_type_dd');

                toastr.success(data1.message);
            }
        }
    })
})



document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#earning-approve-btn').forEach(function(button) {
        button.onclick = function() {
            $('#earning-approve-id-container').val($(this).attr("data-id"));
        }
    });
});

$('.approve-earning').click(function(event) {
    event.preventDefault()
    var earning_id = $('#earning-approve-id-container').val()
        // console.log(earning_id)
    $.ajax({
        type: "POST",
        url: `earning/approve/${earning_id}`,
        data: {
            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
            earning_id: earning_id
        },
        success: function(data1) {

            if (data1.status == "error") {
                // alert(data1.message)
                $('#earning-approve').modal('hide')
                $(`.approve-deny-${earning_id}`).html("")
                toastr.error(data1.message);
            } else if (data1.status == "success") {
                //alert(data1.message)
                $('#earning-approve').modal('hide')
                $(`.earning-approve-deny-${earning_id}`).html("")
                    // select = document.getElementById('#os_type_dd');

                toastr.success(data1.message);
            }
        }
    })
})

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#earning-deny-btn').forEach(function(button) {
        button.onclick = function() {
            $('#earning-deny-id-container').val($(this).attr("data-id"));
        }
    });
});

$('.deny-earning').click(function(event) {
    event.preventDefault()
    var earning_id = $('#earning-deny-id-container').val()
        // console.log(earning_id)
    $.ajax({
        type: "POST",
        url: `earning/deny/${earning_id}`,
        data: {
            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
            earning_id: earning_id
        },
        success: function(data1) {

            if (data1.status == "error") {
                // alert(data1.message)
                $('#earning-deny').modal('hide')
                $(`.earning-approve-deny-${earning_id}`).html("")
                toastr.error(data1.message);
            } else if (data1.status == "success") {
                //alert(data1.message)
                $('#earning-deny').modal('hide')
                $(`.earning-approve-deny-${earning_id}`).html("")
                    // select = document.getElementById('#os_type_dd');

                toastr.success(data1.message);
            }
        }
    })
})

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#expenditure-deny-btn').forEach(function(button) {
        button.onclick = function() {
            $('#expenditure-deny-id-container').val($(this).attr("data-id"));
        }
    });
});

$('.deny-expenditure').click(function(event) {
    event.preventDefault()
    var expenditure_id = $('#expenditure-deny-id-container').val()
        // console.log(earning_id)
    $.ajax({
        type: "POST",
        url: `expenditure/deny/${expenditure_id}`,
        data: {
            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
            expenditure_id: expenditure_id
        },
        success: function(data1) {

            if (data1.status == "error") {
                // alert(data1.message)
                $('#expenditure-deny').modal('hide')
                $(`.expenditure-approve-deny-${expenditure_id}`).html("")
                toastr.error(data1.message);
            } else if (data1.status == "success") {
                //alert(data1.message)
                $('#expenditure-deny').modal('hide')
                $(`.expenditure-approve-deny-${expenditure_id}`).html("")
                    // select = document.getElementById('#os_type_dd');

                toastr.success(data1.message);
            }
        }
    })
})

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#expenditure-approve-btn').forEach(function(button) {
        button.onclick = function() {
            $('#expenditure-approve-id-container').val($(this).attr("data-id"));
        }
    });
});

$('.approve-expenditure').click(function(event) {
    event.preventDefault()
    var expenditure_id = $('#expenditure-approve-id-container').val()
        // console.log(earning_id)
    $.ajax({
        type: "POST",
        url: `expenditure/approve/${expenditure_id}`,
        data: {
            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
            expenditure_id: expenditure_id
        },
        success: function(data1) {

            if (data1.status == "error") {
                // alert(data1.message)
                $('#expenditure-approve').modal('hide')
                $(`.expenditure-approve-deny-${expenditure_id}`).html("")
                toastr.error(data1.message);
            } else if (data1.status == "success") {
                //alert(data1.message)
                $('#expenditure-approve').modal('hide')
                $(`.expenditure-approve-deny-${expenditure_id}`).html("")
                    // select = document.getElementById('#os_type_dd');

                toastr.success(data1.message);
            }
        }
    })
})

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#disable-user-btn').forEach(function(button) {
        button.onclick = function() {
            $('#disable-user-id-container').val($(this).attr("data-id"));
        }
    });
});

$('.disable-user-submit').click(function(event) {
    event.preventDefault()
    var user_id = $('#disable-user-id-container').val()
        // console.log(earning_id)
    $.ajax({
        type: "POST",
        url: `disable/member/${user_id}/`,
        data: {
            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
        },
        success: function(data1) {

            if (data1.status == "error") {
                // alert(data1.message)
                $('#disable-user').modal('hide')
                toastr.error(data1.message);
            } else if (data1.status == "success") {
                //alert(data1.message)
                $('#disable-user').modal('hide')
                $(`.user-enable-disable-${user_id}`).html("Disabled")
                    // select = document.getElementById('#os_type_dd');

                toastr.success(data1.message);
            }
        }
    })
})

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#enable-user-btn').forEach(function(button) {
        button.onclick = function() {
            $('#enable-user-id-container').val($(this).attr("data-id"));
        }
    });
});

$('.enable-user-submit').click(function(event) {
    event.preventDefault()
    var user_id = $('#enable-user-id-container').val()
        // console.log(earning_id)
    $.ajax({
        type: "POST",
        url: `enable/member/${user_id}/`,
        data: {
            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
        },
        success: function(data1) {

            if (data1.status == "error") {
                // alert(data1.message)
                $('#enable-user').modal('hide')
                toastr.error(data1.message);
            } else if (data1.status == "success") {
                // alert(data1.message)
                $('#enable-user').modal('hide')
                $(`.user-enable-disable-${user_id}`).html("Enabled")
                    // select = document.getElementById('#os_type_dd');

                toastr.success(data1.message);
            }
        }
    })
})

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#member-user-btn').forEach(function(button) {
        button.onclick = function() {
            $('#member-user-id-container').val($(this).attr("data-id"));
        }
    });
});

$('.member-user-submit').click(function(event) {
    event.preventDefault()
    var user_id = $('#member-user-id-container').val()
        // console.log(earning_id)
    $.ajax({
        type: "POST",
        url: `make/member/${user_id}/`,
        data: {
            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
        },
        success: function(data1) {

            if (data1.status == "error") {
                // alert(data1.message)
                $('#member-user').modal('hide')
                toastr.error(data1.message);
            } else if (data1.status == "success") {
                // alert(data1.message)
                $('#member-user').modal('hide')
                $(`.admin-enable-disable-${user_id}`).html("Member")
                    // select = document.getElementById('#os_type_dd');

                toastr.success(data1.message);
            }
        }
    })
})

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#admin-user-btn').forEach(function(button) {
        button.onclick = function() {
            $('#admin-user-id-container').val($(this).attr("data-id"));
        }
    });
});

$('.admin-user-submit').click(function(event) {
    event.preventDefault()
    var user_id = $('#admin-user-id-container').val()
        // console.log(earning_id)
    $.ajax({
        type: "POST",
        url: `make/admin/${user_id}/`,
        data: {
            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
        },
        success: function(data1) {

            if (data1.status == "error") {
                // alert(data1.message)
                $('#admin-user').modal('hide')
                toastr.error(data1.message);
            } else if (data1.status == "success") {
                // alert(data1.message)
                $('#admin-user').modal('hide')
                $(`.admin-enable-disable-${user_id}`).html("Admin")
                    // select = document.getElementById('#os_type_dd');

                toastr.success(data1.message);
            }
        }
    })
})

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#archive-announcement-btn').forEach(function(button) {
        button.onclick = function() {
            $('#archive-announcement-id-container').val($(this).attr("data-id"));

        }
    });
});

$('.archive-announcement-submit').click(function(event) {
    event.preventDefault()
    var ann_id = $('#archive-announcement-id-container').val()
        // console.log(earning_id)
    $.ajax({
        type: "POST",
        url: `unpublish/announcement/${ann_id}/`,
        data: {
            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
        },
        success: function(data1) {

            if (data1.status == "error") {
                // alert(data1.message)
                $('#archive-announcement').modal('hide')
                toastr.error(data1.message);
            } else if (data1.status == "success") {
                // alert(data1.message)
                $('#archive-announcement').modal('hide')
                $(`.archive-announcement-${ann_id}`).html(`Archived`)
                    // select = document.getElementById('#os_type_dd');

                toastr.success(data1.message);
            }
        }
    })
})

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#activate-announcement-btn').forEach(function(button) {
        button.onclick = function() {
            $('#activate-announcement-id-container').val($(this).attr("data-id"));

        }
    });
});

$('.activate-announcement-submit').click(function(event) {
    event.preventDefault()
    var ann_id = $('#activate-announcement-id-container').val()
        // console.log(earning_id)
    $.ajax({
        type: "POST",
        url: `publish/announcement/${ann_id}/`,
        data: {
            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
        },
        success: function(data1) {

            if (data1.status == "error") {
                // alert(data1.message)
                $('#archive-announcement').modal('hide')
                toastr.error(data1.message);
            } else if (data1.status == "success") {
                // alert(data1.message)
                $('#activate-announcement').modal('hide')
                $(`.archive-announcement-${ann_id}`).html('Active')
                    // select = document.getElementById('#os_type_dd');

                toastr.success(data1.message);
            }
        }
    })
})