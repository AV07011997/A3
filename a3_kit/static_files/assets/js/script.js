$('a.dropdown-toggle').on('click', function(e) {
    e.preventDefault();
    $('.dropdown-menu').slideToggle();
});

$('.add-new').on('click', function(e) {
    e.preventDefault();
    deal_id = "";
    customer_id = "";
    var dist_id = [126,127,128,588,589,590, 1022, 1023, 1025];
    var dist_name = ['NORTH EAST DELHI', 'NORTH WEST DELHI', 'SOUTH DELHI', 'DEHRADUN', 'HARIDWAR', 'NAINITAL', 'RUPNAGAR', 'SAHIBZA AJIT SINGH NAGAR', 'PATIALA'];
    var dist_html = '<select name="dist" id="dist" style="max-width:90%;">';
    // +'<option value="none">Select district</option>';
    for( var i = 0; i < dist_id.length; i++){
        dist_html = dist_html.concat('<option value="'+dist_id[i]+','+dist_name[i]+'">' + dist_name[i] + '</option>');
    }
    dist_html.concat('</select>');


    var state_id = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,28,34];
    var state_name = ['ANDAMAN & NICOBAR','ANDHRA PRADESH','ARUNACHAL PRADESH','ASSAM','BIHAR','CHANDIGARH','CHHATTISGARH','DADRA AND NAGAR HAVELI','DAMAN AND DIU','DELHI', 'GOA', 'GUJRAT', 'HARYANA', 'HIMACHAL PRADESH','JAMMU & KASHMIR','PUNJAB','UTTARAKHAND'];
    var state_html = '<select name="state" id="state" style="max-width:90%;">';
    // +'<option value="none">Select district</option>';
    for( var i = 0; i < state_id.length; i++){
        state_html = state_html.concat('<option value="'+state_id[i]+','+state_name[i]+'">' + state_name[i] + '</option>');
    }
    state_html.concat('</select>');


    var bank_id = [1,2,3,4,5,6,7,8];
    var bank_name = ['ALLAHABAD BANK', 'ANDHRA BANK', 'AXIS BANK LTD', 'BANK OF AMERICA', 'BANK OF BARODA', 'PUNJAB NATIONAL BANK', 'STATE BANK OF INDIA', 'ICICI'];
    var bank_html = '<select name="bank" id="bank" style="max-width:90%;">';
    // +'<option value="none">Select district</option>';
    for( var i = 0; i < bank_id.length; i++){
        bank_html = bank_html.concat('<option value="'+bank_id[i]+','+bank_name[i]+'">' + bank_name[i] + '</option>');
    }
    bank_html.concat('</select>');


    $('.table_wrap.loan table').append(
    '<tr>' + 
    '<td><input type="radio" name="loan" class="loan_selector" value="" checked /></td>' +
    '<td><input name="deal_id" class="form-control" type="text"></td>' +
    '<td><input name="customer_id" class="form-control" type="text"></td>' +
    '<td><input name="name" class="form-control" type="text"></td>' +
    '<td><input name="dob" class="form-control" type="text"></td>' +
    '<td><input name="aadhaar" class="form-control" type="text"></td>' +
    // '<td><input name="district" class="form-control" type="text"></td>' +
    '<td>'+dist_html+'</td>' +
    // '<td><input name="state" class="form-control" type="text"></td>' +
    '<td>'+state_html+'</td>' +
    '<td><input name="pin_code" class="form-control" type="text"></td>' +
    // '<td><input name="bank_name" class="form-control" type="text"></td>' +
    '<td>'+bank_html+'</td>' +
    '<td><input name="account_no" class="form-control" type="text"></td>' +
    '</tr>'
    );

    document.getElementsByClassName("add-new")[0].disabled = true;
    
});

$('a.upload-section-close').on('click', function(e) {
    e.preventDefault();
    $(this).closest('.upload-section').toggle();
});



$('body').on('click', 'a.upload', function(e) {
    e.preventDefault();
    var thisElem = $(this).closest('.upload-section-wrap');
    $(thisElem)('.imgInp').trigger('click');
})

// $('a.uploadNow').on('click', function(e) {
//     e.preventDefault();
// })

$(".imgInp").change(function() {
    if (this.files) {
        var thisElem = $(this).closest('.upload-section-wrap');
        for (var i = 0; i < this.files.length; i++) {
            var reader = new FileReader();
            var file = this.files[i];
            reader.onload = function(e) {
                //$('#blah').attr('src', e.target.result);
                addPanAadhaarFiles(e.target.result, file.name, (file.size / 1024).toFixed(2), thisElem, 0);
            }
            reader.readAsDataURL(this.files[i]);
        }
    }
});

function addPanAadhaarFiles(url, name, size, thisElem, isImageExists) {
    file_type = name.split('.').pop();
    console.log("name:", name);
    console.log("ext:", file_type);
    console.log("isImageExists", isImageExists);
    if(file_type == 'pdf'){
        if(isImageExists == 1){
            $("#submit_file_btn2").css("display", "none");
            $(thisElem).find('.files-wrap').append('<div class="single-file">'+
            '<div class="img-section"><object id="pdf_viewer" frameborder="0" scrolling="no"  data='+ url +'#zoom=FitH style="width: 100%;height: 100%; overflow: auto;"></object></div>'
            +'<h5>' + name + '<br/></h5><div class="buttons"><div class="row"><div style="visibility: hidden;" class="col-6"><a class="upload" href="#"><i class="lni lni-circle-plus"></i></a></div><div class="col-6 text-right"><a style="display: none;" class="upload" href="#"><i class="lni lni-upload"></i></a><a onclick="removePanAadhaar()" ><i class="lni lni-trash"></i></a><a data-caption="' + name + '" onclick="openPdfPopup(\'' + url + '\')"><i class="fa fa-search-plus" aria-hidden="true"></i></a></div></div></div></div>');
        }
        else if(isImageExists == 0){
            $(thisElem).find('.files-wrap').append('<div class="single-file">'+
            '<div class="img-section"><object id="pdf_viewer" frameborder="0" scrolling="no"  data='+ url +'#zoom=FitH style="width: 100%;height: 100%; overflow: auto;"></object></div>'
            +'<h5>' + name + '<br/></h5><div class="buttons"><div class="row"><div style="visibility: hidden;" class="col-6"><a class="upload" href="#"><i class="lni lni-circle-plus"></i></a></div><div class="col-6 text-right"><a class="upload" onclick="uploadPanAadhaar()"><i class="lni lni-upload"></i></a><a onclick="removePanAadhaar()"><i class="lni lni-trash"></i></a><a data-caption="' + name + '" onclick="openPdfPopup(\'' + url + '\')"><i class="fa fa-search-plus" aria-hidden="true"></i></a></div></div></div></div>');
        }
        // +'<h5>' + name + '<br/></h5><div class="buttons"><div class="row"><div class="col-6"><a class="upload" href="#"><i class="lni lni-circle-plus"></i></a></div><div class="col-6 text-right"><a class="upload" href="#"><i class="lni lni-upload"></i></a><a class="remove" href="#"><i class="lni lni-trash"></i></a><a href="' + url + '" data-fancybox="gallery" data-caption="' + name + '" href="#"><i class="fa fa-search-plus" aria-hidden="true"></i></a></div></div></div></div>');
    }
    else{
        if(isImageExists == 1){
            $("#submit_file_btn2").css("display", "none");
            $(thisElem).find('.files-wrap').append('<div class="single-file"><div class="img-section" style="background-image: url(' + url + ');"></div><h5>' + name + '<br/></h5><div class="buttons"><div class="row"><div style="visibility: hidden;" class="col-6"><a class="upload" href="#"><i class="lni lni-circle-plus"></i></a></div><div class="col-6 text-right"><a style="display: none;" class="upload" href="#"><i class="lni lni-upload"></i></a><a class="remove" onclick="removePanAadhaar()" href="#"><i class="lni lni-trash"></i></a><a href="' + url + '" data-fancybox="gallery" data-caption="' + name + '" href="#"><i class="fa fa-search-plus" aria-hidden="true"></i></a></div></div></div></div>');
        }
        else if(isImageExists == 0){
            console.log("image not exists.");
            $(thisElem).find('.files-wrap').append('<div class="single-file"><div class="img-section" style="background-image: url(' + url + ');"></div><h5>' + name + '<br/></h5><div class="buttons"><div class="row"><div style="visibility: hidden;" class="col-6"><a class="upload" href="#"><i class="lni lni-circle-plus"></i></a></div><div class="col-6 text-right"><a class="upload" href="#" onclick="uploadPanAadhaar()"><i class="lni lni-upload"></i></a><a class="remove" onclick="removePanAadhaar()" href="#"><i class="lni lni-trash"></i></a><a href="' + url + '" data-fancybox="gallery" data-caption="' + name + '" href="#"><i class="fa fa-search-plus" aria-hidden="true"></i></a></div></div></div></div>');
        }
    }
    count(thisElem, "pan_aadhaar");
}

// $('a.remove_pan_aadhaar').on('click', function(e) {
//     console.log("delete btn clicked");
//     console.log("imageExists", imageExists);

//     // if(imageExists == 0){
//     //     var thisElem = $(this).closest('.upload-section-wrap');
//     //     $(thisElem).find('.files-wrap').html('');
//     //     e.preventDefault();
//     //     count(thisElem);
//     // }
    
// })


function uploadPanAadhaar(){
    console.log("upload pan aadhaar btn clicked.");
    // var formData = new FormData(document.getElementById("pan_aadhar"));//$("#pan_aadhar").serializeArray();
    var formData = new FormData();
    var token = $('[name=csrfmiddlewaretoken]').val();
    var file_data = $('#uploadfile')[0].files[0];
    formData.append("csrfmiddlewaretoken", token);
    formData.append('file_upload', file_data);
    console.log(formData);
    var url_dict = {"PAN":"/pan/processing/", "Aadhaar":"/aadhaar/processing/"};
    console.log(url_dict[doc_type]);
    document.getElementById('popupMessage1').innerHTML = '<br>Processing...<br>';
    
    $("#popupconfirm").attr("style", "display: none;");
    $("#messageAcknowledge").attr("style", "display: none;");
    $("#selectdealid").attr("style", "display: none;");
    $('#triggerPopup').modal('show');
    $.ajax({
        url: url_dict[doc_type],
        data: formData,
        type: 'POST',
        contentType: false, 
        processData: false, 
        success: function(res){
            // alert("success");
            console.log(JSON.parse(res));
            response = JSON.parse(res);
            if (response.status["type"]=="success")
            {
                // console.log("file upload sucess");
                // location.reload();
                document.getElementById('popupMessage1').innerHTML = '<br>' + response.status["message"] + '<br>';
                document.getElementById('messageAcknowledge').innerHTML = 'OK';
                $("#popupconfirm").attr("style", "display: none;");
                $("#selectdealid").attr("style", "display: none;");
                $("#messageAcknowledge").removeAttr('style');
                $('#triggerPopup').modal('show');
            } 
            else if (response.status["type"]=="other"){
                // console.log("file upload others");
                document.getElementById('popupMessage1').innerHTML = response.status["message"];
                document.getElementById('messageAcknowledge').innerHTML = 'OK';
                $("#popupconfirm").attr("style", "display: none;");
                $("#selectdealid").attr("style", "display: none;");
                $("#messageAcknowledge").removeAttr('style');
                $('#triggerPopup').modal('show');
            }
            else if (response.status["type"]=="deal"){
                // console.log("file upload others");
                document.getElementById('popupMessage1').innerHTML = response.status["message"];
                document.getElementById('selectdealid').innerHTML = 'OK';
                $("#popupconfirm").attr("style", "display: none;");
                $("#selectdealid").removeAttr('style');
                $("#messageAcknowledge").attr("style", "display: none;");
                $('#triggerPopup').modal('show');
            }
            else {
                // console.log("file upload else");
                document.getElementById('popupMessage1').innerHTML = response.status["message"];
                document.getElementById('messageAcknowledge').innerHTML = 'cancel';
                $("#popupconfirm").removeAttr('style');
                $("#selectdealid").attr("style", "display: none;");
                $("#messageAcknowledge").removeAttr('style');
                $('#triggerPopup').modal('show');
            }
        },
    });

}



function removePanAadhaar(){
    console.log("delete btn clicked");
    console.log("imageExists", imageExists);
    if(imageExists == 0){
        console.log("no image exists");
        location.reload();
    }
    else{
        console.log("image exists");
        console.log("name of the image: ", image_name);
        var url_dict = {"PAN":"/remove_pan_image/", "Aadhaar":"/remove_aadhaar_image/"};
        // var url_map = {"PAN":"pan", "Aadhaar":"aadhaar"};
        var token = $('[name=csrfmiddlewaretoken]').val();
        var formData = new FormData();
        formData.append("csrfmiddlewaretoken", token);
        formData.append('file_name', image_name);
        console.log(url_dict[doc_type]);
        $.ajax({
            url: url_dict[doc_type],
            data: formData,
            type: 'POST',
            contentType: false, 
            processData: false, 
            success: function(response){
                if(response == "success"){
                    location.reload();
                    // alert("successfully deleted");
                }
                else{
                    location.reload();
                    alert("Something wrong, please try again.");
                }
            },
            error: function(response){
                location.reload();
                alert("Something wrong, please try again.");
            },
        });
        
        // location.reload();

    }
}




function openPdfPopup(url){
    console.log("pdf popup called");
    // console.log(url);
    document.getElementById("pdf_obj").innerHTML='';
    document.getElementById("pdf_obj").innerHTML='<object frameborder="0" scrolling="no" data="'+url+'" style="width: 100%;height: 100%;"></object>';
    // // $('#pdf_obj').data(url);
    $('#pdf_popup').modal('show');
}



$(".imgInp1").change(function() {
    var doc_id = $("#year_1").val();
    if (this.files) {
        var thisElem = $(this).closest('.upload-section-wrap');
        for (var i = 0; i < this.files.length; i++) {
            var reader = new FileReader();
            var file = this.files[i];
            reader.onload = function(e) {
                //$('#blah').attr('src', e.target.result);
                addFiles(e.target.result, file.name, (file.size / 1024).toFixed(2), thisElem, 1, doc_id, 0);
            }
            reader.readAsDataURL(this.files[i]);
        }
    }
});

$(".imgInp2").change(function() {
    var doc_id = $("#year_2").val();
    if (this.files) {
        var thisElem = $(this).closest('.upload-section-wrap');
        for (var i = 0; i < this.files.length; i++) {
            var reader = new FileReader();
            var file = this.files[i];
            reader.onload = function(e) {
                //$('#blah').attr('src', e.target.result);
                addFiles(e.target.result, file.name, (file.size / 1024).toFixed(2), thisElem, 2, doc_id, 0);
            }
            reader.readAsDataURL(this.files[i]);
        }
    }
});

$(".imgInp3").change(function() {
    var doc_id = $("#year_3").val();
    if (this.files) {
        var thisElem = $(this).closest('.upload-section-wrap');
        for (var i = 0; i < this.files.length; i++) {
            var reader = new FileReader();
            var file = this.files[i];
            reader.onload = function(e) {
                //$('#blah').attr('src', e.target.result);
                addFiles(e.target.result, file.name, (file.size / 1024).toFixed(2), thisElem, 3, doc_id, 0);
            }
            reader.readAsDataURL(this.files[i]);
        }
    }
});




// var imageExists = 0; 
function addFiles(url, name, size, thisElem, no, doc_id, imageExists) {
    console.log("name: ", name);
    console.log("imageExists: ", imageExists);
    console.log("add files: ", doc_id)
    var doc_name = {"3":"Itr-V", "4":"Form 16", "5":"form 26as"};
    // var doc_id = $('#year_'+no).val();
    if (imageExists == 1){
        $(thisElem).find('.files-wrap').append('<div class="single-file">'+
        // <div class="img-section" style="background-image: url(' + url + ');"></div>
        '<div class="img-section"><object id="pdf_viewer" frameborder="0" scrolling="no"  data='+ url +'#zoom=FitH style="width: 100%;height: 100%; overflow: auto;"></object></div>'
        +'<p>' + doc_name[doc_id] + '</p><h5>' + name + '<br/>(' + size + 'KB)</h5><div class="buttons"><div class="row"><div class="col-6"><a style="visibility: hidden;" class="upload" href="#"><i class="lni lni-circle-plus"></i></a></div><div class="col-6 text-right"><a style="display:none;" class="upload" href="#" onclick="upload_files('+no+')"><i class="lni lni-upload"></i></a><a class="remove" onclick="removeItrvForm16Form26as(\''+ name +'\', '+ imageExists +', '+ doc_id +')"><i class="lni lni-trash"></i></a><a href="' + url + '" data-fancybox="gallery" data-caption="' + name + ' (' + size + 'KB)" href="#"><i class="fa fa-search-plus" aria-hidden="true"></i></a></div></div></div></div>');    
    }
    else{
        $(thisElem).find('.files-wrap').append('<div class="single-file">'+
        // <div class="img-section" style="background-image: url(' + url + ');"></div>
        '<div class="img-section"><object id="pdf_viewer" frameborder="0" scrolling="no"  data='+ url +'#zoom=FitH style="width: 100%;height: 100%; overflow: auto;"></object></div>'
        +'<p>' + doc_name[doc_id] + '</p><h5>' + name + '<br/>(' + size + 'KB)</h5><div class="buttons"><div class="row"><div class="col-6"><a style="visibility: hidden;" class="upload" href="#"><i class="lni lni-circle-plus"></i></a></div><div class="col-6 text-right"><a class="upload" href="#" onclick="upload_files('+no+')"><i class="lni lni-upload"></i></a><a class="remove" onclick="removeItrvForm16Form26as(\''+ name +'\', '+ imageExists +', '+ doc_id +')"><i class="lni lni-trash"></i></a><a id="zoom_file'+ no +'" onclick="openPdfPopup(\'' + url + '\')" data-caption="' + name + ' (' + size + 'KB)" href="#"><i class="fa fa-search-plus" aria-hidden="true"></i></a></div></div></div></div>');    
    }
    
    count(thisElem, "itr_form_16_26");
}


function upload_files(no){
    console.log("upload itvr clicked");

    var url_dict = {"3":"/itrv/processing/", "4":"/form16/processing/", "5":"/form26as/processing/"};
    var doc_type = $('#year_'+no).val();
    var file_data = $('#uploadfile'+no)[0].files[0];
    // console.log($('#uploadfile'+no)[0].files[0]);
    // console.log(file_data);
    // document_type = $('#year_'+no).val();
    var token = $('[name=csrfmiddlewaretoken]').val();
    // console.log(token);
    var formData = new FormData();
    formData.append("csrfmiddlewaretoken", token);
    formData.append('file_upload', file_data);
    formData.append('document_type', doc_type);
    formData.append('year', no);

    document.getElementById('popupMessage').innerHTML = '<br>Processing...<br>';
    $("#popupconfirm").attr("style", "display: none;");
    $("#messageAcknowledge").attr("style", "display: none;");
    $('#triggerPopup').modal('show');
    
    $.ajax({
        url: url_dict[doc_type],
        data: formData,
        type: 'POST',
        contentType: false, 
        processData: false, 
        success: function(res){
            // alert("success");
            response = JSON.parse(res);
            if (response.status["type"]=="success")
            {
                document.getElementById('popupMessage').innerHTML = '<br>' + response.status["message"] + '<br>';
                document.getElementById('messageAcknowledge').innerHTML = 'OK';
                $("#popupconfirm").attr("style", "display: none;");
                $("#messageAcknowledge").removeAttr('style');
                $('#triggerPopup').modal('show');
            } else if (response.status["type"]=="other")
            {
                document.getElementById('popupMessage').innerHTML = response.status["message"];
                document.getElementById('messageAcknowledge').innerHTML = 'OK';
                $("#popupconfirm").attr("style", "display: none;");
                $("#messageAcknowledge").removeAttr('style');
                $('#triggerPopup').modal('show');
            }
            else {
                document.getElementById('popupMessage').innerHTML = response.status["message"];
                $("#popupconfirm").removeAttr('style');
                $("#messageAcknowledge").removeAttr('style');
                $('#triggerPopup').modal('show');
            }
        },
    });
}



function removeItrvForm16Form26as(name, fileExists, doc_type_id){
    console.log("file name to be deleted: "+name);
    if(fileExists == 1){
        var url_dict = {"3":"/remove_itrv_image/", "4":"/remove_form16_image/", "5":"/remove_form26as_image/"};
        // var url_map = {"PAN":"pan", "Aadhaar":"aadhaar"};
        var token = $('[name=csrfmiddlewaretoken]').val();
        var formData = new FormData();
        formData.append("csrfmiddlewaretoken", token);
        formData.append('file_name', name);
        console.log(url_dict[doc_type_id]);
        $.ajax({
            url: url_dict[doc_type_id],
            data: formData,
            type: 'POST',
            contentType: false, 
            processData: false, 
            success: function(response){
                if(response == "success"){
                    location.reload();
                    // alert("successfully deleted");
                }
                else{
                    location.reload();
                    alert("Something wrong, please try again.");
                }
            },
            error: function(response){
                location.reload();
                alert("Something wrong, please try again.");
            },
        });
    }
    else{
        location.reload();
    }
}



function count(thisElem, formType) {
    if ($(thisElem).find('.files-wrap .single-file').length > 0) {
        $(thisElem).find('.upload-section-inner h3').hide();
        $(thisElem).find(".upload-form").removeClass('not-selected');
        if ($(thisElem).find('.files-wrap .single-file').length == 1) {
            var file = 'file';
        } else {
            var file = 'files';
        }
        $(thisElem).find('.upload-form .form-box').html('<i style="font-size: 20px; margin-right: 10px;" class="fa fa-file-o" aria-hidden="true"></i>&nbsp;' + $(thisElem).find('.files-wrap .single-file').length + ' ' + file + ' selected');
    } else {
        $(thisElem).find('.upload-section-inner h3').show();
        $(thisElem).find(".upload-form").addClass('not-selected');
        $(thisElem).find('.upload-form .form-box').html('Select Files...');
    }
    if (formType == "pan_aadhaar" && $(thisElem).find('.files-wrap .single-file').length >= 1)
    {
        // disabled upload when 1 file is alrealry there for pan or aadhaar
        $("#uploadfile").attr("disabled","disabled");
    }
}

// $('a.removeAll').on('click', function(e) {
//     var thisElem = $(this).closest('.upload-section-wrap');
//     $(thisElem).find('.files-wrap').html('');
//     e.preventDefault();
//     count(thisElem);
// })

// $('body').on('click', 'a.remove', function(e) {
//     e.preventDefault();
//     var thisElem = $(this).closest('.upload-section-wrap');
//     $(this).closest('.single-file').remove();
//     count(thisElem);
// })

$('body').on('click', 'a.view', function(e) {
    e.preventDefault();
})

$(document).ready(function() {
    jQuery('.date_picker').datetimepicker({
        timepicker: false,
        format: 'd-m-Y'
    });
})

$(document).ready(function() {
    function alignModal() {
        var modalDialog = $(this).find(".modal-dialog");

        // Applying the top margin on modal to align it vertically center
        modalDialog.css("margin-top", Math.max(0, ($(window).height() - modalDialog.height()) / 2));
    }
    // Align modal when it is displayed
    $(".modal").on("shown.bs.modal", alignModal);

    // Align modal when user resize the window
    $(window).on("resize", function() {
        $(".modal:visible").each(alignModal);
    });
});

// Bank Statement upload
$(".imgInpb1").change(function() {
    if (this.files) {
        var extract_radio = document.getElementById("extract_bank1").checked;
        var upload_radio = document.getElementById("upload_bank1").checked;
        if(extract_radio == true){
            action_type = 0;
        }
        if(upload_radio == true){
            action_type = 1;
        }
        var bank_name = $('#bank_nameb1').val();
        bank_name_id = {'BOB':'5', 'CBI':'9', 'HDFC':'10', 'IDFC':'11', 'OBC':'12'};
        bank_id = bank_name_id[bank_name];
        var thisElem = $(this).closest('.upload-section-wrap');
        for (var i = 0; i < this.files.length; i++) {
            var reader = new FileReader();
            var file = this.files[i];
            reader.onload = function(e) {
                //$('#blah').attr('src', e.target.result);
                addbsFiles(e.target.result, file.name, (file.size / 1024).toFixed(2), thisElem, 1, bank_id, action_type, 0);
            }
            reader.readAsDataURL(this.files[i]);
        }
    }
});


$(".imgInpb2").change(function() {
    if (this.files) {
        var extract_radio = document.getElementById("extract_bank2").checked;
        var upload_radio = document.getElementById("upload_bank2").checked;
        if(extract_radio == true){
            action_type = 0;
        }
        if(upload_radio == true){
            action_type = 1;
        }
        var bank_name = $('#bank_nameb2').val();
        bank_name_id = {'BOB':'5', 'CBI':'9', 'HDFC':'10', 'IDFC':'11', 'OBC':'12'};
        bank_id = bank_name_id[bank_name];
        var thisElem = $(this).closest('.upload-section-wrap');
        for (var i = 0; i < this.files.length; i++) {
            var reader = new FileReader();
            var file = this.files[i];
            reader.onload = function(e) {
                //$('#blah').attr('src', e.target.result);
                addbsFiles(e.target.result, file.name, (file.size / 1024).toFixed(2), thisElem, 2, bank_id, action_type, 0);
            }
            reader.readAsDataURL(this.files[i]);
        }
    }
});

$(".imgInpb3").change(function() {
    if (this.files) {
        var extract_radio = document.getElementById("extract_bank3").checked;
        var upload_radio = document.getElementById("upload_bank3").checked;
        if(extract_radio == true){
            action_type = 0;
        }
        if(upload_radio == true){
            action_type = 1;
        }
        var bank_name = $('#bank_nameb3').val();
        bank_name_id = {'BOB':'5', 'CBI':'9', 'HDFC':'10', 'IDFC':'11', 'OBC':'12'};
        bank_id = bank_name_id[bank_name];

        var thisElem = $(this).closest('.upload-section-wrap');
        for (var i = 0; i < this.files.length; i++) {
            var reader = new FileReader();
            var file = this.files[i];
            reader.onload = function(e) {
                //$('#blah').attr('src', e.target.result);
                addbsFiles(e.target.result, file.name, (file.size / 1024).toFixed(2), thisElem, 3, bank_id, action_type, 0);
            }
            reader.readAsDataURL(this.files[i]);
        }
    }
});

function addbsFiles(url, name, size, thisElem, no, bank_id, action_type, imageExists) {
    bank_id_name = {'5':'BOB', '9':'CBI', '10':'HDFC', '11':'IDFC', '12':'OBC'};
    if(imageExists == 1){
        console.log("imageExists", imageExists);
        console.log("bank name", bank_id_name[bank_id]);
        console.log("bank no", no);
        console.log("bank file name", name);

        console.log("bank file url", url);
        $(thisElem).find('.files-wrap').append('<div class="single-file">'+
        '<div class="img-section"><object id="pdf_viewer" frameborder="0" scrolling="no"  data='+ url +'#zoom=FitH style="width: 100%;height: 100%; overflow: auto;"></object></div>'
        +'<p>' + bank_id_name[bank_id] + '</p><h5>' + name + '<br/></h5><div class="buttons"><div class="row"><div class="col-6"><a style="visibility: hidden;" class="upload" href="#"><i class="lni lni-circle-plus"></i></a></div><div class="col-6 text-right"><a style="display: none;" class="upload" href="#" onclick="upload_bs_files('+"'"+no+"'"+')"><i class="lni lni-upload"></i></a><a class="remove" onclick="removeBankStatement(\''+ name +'\', '+ imageExists +')"><i class="lni lni-trash"></i></a><a onclick="openPdfPopup(\'' + url + '\')" data-caption="' + name + ' (' + size + 'KB)" ><i class="fa fa-search-plus" aria-hidden="true"></i></a></div></div></div></div>');

    }
    else if (imageExists == 0){
        $(thisElem).find('.files-wrap').append('<div class="single-file">'+
        '<div class="img-section"><object id="pdf_viewer" frameborder="0" scrolling="no"  data='+ url +'#zoom=FitH style="width: 100%;height: 100%; overflow: auto;"></object></div>'
        +'<h5>' + name + '<br/>(' + size + 'KB)</h5><div class="buttons"><div class="row"><div class="col-6"><a style="visibility: hidden;" class="upload" href="#"><i class="lni lni-circle-plus"></i></a></div><div class="col-6 text-right"><a class="upload" href="#" onclick="upload_bs_files('+"'"+no+"'"+')"><i class="lni lni-upload"></i></a><a class="remove" onclick="removeBankStatement(\''+ name +'\', '+ imageExists +')"><i class="lni lni-trash"></i></a><a onclick="openPdfPopup(\'' + url + '\')" data-caption="' + name + ' (' + size + 'KB)" ><i class="fa fa-search-plus" aria-hidden="true"></i></a></div></div></div></div>');
    
    }
    count(thisElem, "bank");

    
}


function upload_bs_files(no){
    console.log("no: ", no);
    var extract_radio = document.getElementById("extract_bank"+no).checked;
    var upload_radio = document.getElementById("upload_bank"+no).checked;

    if(extract_radio == true){
        action_type = 0;
    }
    if(upload_radio == true){
        action_type = 1;
    }
    // console.log(action_type);

    bank_name_id = {'BOB':'5', 'CBI':'9', 'HDFC':'10', 'IDFC':'11', 'OBC':'12'};
    var file_data = $('#uploadfileb'+no)[0].files[0];
    var file_pass = $('#uploadfilepsdb'+no).val();
    var token = $('[name=csrfmiddlewaretoken]').val();
    var bank_name = $('#bank_nameb'+no).val();
    var bank_index = no;
    var bank_id = bank_name_id[bank_name];
    // console.log(token);

    // console.log(bank_name);
    // console.log(bank_index);
    // console.log(bank_id);
    // console.log(file_data);
    // console.log(file_pass);
    // console.log(token);


    var formData = new FormData();
    formData.append("csrfmiddlewaretoken", token);
    formData.append('file_upload', file_data);
    formData.append('action_type', action_type);
    formData.append('bank_index', bank_index);
    formData.append('bank_id', bank_id);
    formData.append('file_pass', file_pass);
    formData.append('bank_name', bank_name);

    document.getElementById('popupMessage').innerHTML = '<br>Processing...<br>';
    $("#submitgivenpassword").attr("style", "display: none;");
    $("#popupconfirm").attr("style", "display: none;");
    $("#messageAcknowledge").attr("style", "display: none;");
    $('#triggerPopup').modal('show');
    
    $.ajax({
        url: "/bank/processing/",
        data: formData,
        type: 'POST',
        contentType: false, // NEEDED, DON'T OMIT THIS (requires jQuery 1.6+)
        processData: false, // NEEDED, DON'T OMIT THIS
        success: function(response){
            // alert(response.status);
            if (response.status["type"]=="success")
            {
                document.getElementById('popupMessage').innerHTML = '<br>' + response.status["message"] + '<br>';
                document.getElementById('messageAcknowledge').innerHTML = 'OK';
                $("#submitgivenpassword").attr("style", "display: none;");
                $("#messageAcknowledge").removeAttr('style');
                $("#givenpassword").attr("style", "display: none;");
                $("#popupconfirm").attr("style", "display: none;");
                $('#triggerPopup').modal('show');

            } else if (response.status["type"]=="other")
            {
                document.getElementById('popupMessage').innerHTML = response.status["message"];
                document.getElementById('messageAcknowledge').innerHTML = 'OK';
                $("#submitgivenpassword").attr("style", "display: none;");
                $("#messageAcknowledge").removeAttr('style');
                $("#givenpassword").attr("style", "display: none;");
                $("#popupconfirm").attr("style", "display: none;");
                $('#triggerPopup').modal('show');
            }
            else {
                document.getElementById('popupMessage').innerHTML = response.status["message"];
                $("#popupconfirm").removeAttr('style');
                $("#messageAcknowledge").removeAttr('style');
                $("#givenpassword").attr("style", "display: none;");
                $("#submitgivenpassword").attr("style", "display: none;");
                $('#triggerPopup').modal('show');
            }
        },
    });
}


function removeBankStatement(name, fileExists){
    console.log("file name to be deleted: "+name);
    if(fileExists == 1){
        // var url_dict = {"3":"/remove_itrv_image/", "4":"/remove_form16_image/", "5":"/remove_form26as_image/"};
        // var url_map = {"PAN":"pan", "Aadhaar":"aadhaar"};
        var token = $('[name=csrfmiddlewaretoken]').val();
        var formData = new FormData();
        formData.append("csrfmiddlewaretoken", token);
        formData.append('file_name', name);
        $.ajax({
            url: "/remove_bank_statements/",
            data: formData,
            type: 'POST',
            contentType: false, 
            processData: false, 
            success: function(response){
                if(response == "success"){
                    location.reload();
                    // alert("successfully deleted");
                }
                else{
                    location.reload();
                    alert("Something wrong, please try again.");
                }
            },
            error: function(response){
                location.reload();
                alert("Something wrong, please try again.");
            },
        });
    }
    else{
        location.reload();
    }
}



// bureau
$(document).ready(function() {
    if ($('.table_wrap.bureau').length > 0) {
        $('.bureau table tbody tr').each(function() {
            $(this).addClass($(this).find('input[name="last_modified_user"]').val());
        });

        $('.bureau table input[type="radio"]').on('change', function() {
            $('.bureau table input[type="radio"]').each(function() {
                if ($(this).is(':checked')) {
                    $(this).closest('tr').addClass('active');
                } else {
                    $(this).closest('tr').removeClass('active');
                }
            })
        });

        $('.tenure, .roi, .emi').on('input', function() {
            //$(this).closest('tr').find('.current_balance span').text('0');
        });

        $('body').on('click', '.table_wrap.bureau a.reset', function(e) {
            e.preventDefault();
            $(this).closest('tr').find('input[type="radio"]').prop('checked', false);
            $(this).closest('tr').find('input[type="text"]').val('');
        });
    }
});


// //analyze

// /* When the user clicks on the button, 
// toggle between hiding and showing the dropdown content */
// function myFunction() {
//   document.getElementById("myDropdown").classList.toggle("show");
// }

// // Close the dropdown if the user clicks outside of it
// window.onclick = function(event) {
//   if (!event.target.matches('.dropbtn')) {
//     var dropdowns = document.getElementsByClassName("dropdown-content");
//     var i;
//     for (i = 0; i < dropdowns.length; i++) {
//       var openDropdown = dropdowns[i];
//       if (openDropdown.classList.contains('show')) {
//         openDropdown.classList.remove('show');
//       }
//     }
//   }
// }
