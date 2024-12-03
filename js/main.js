$(function(){
  $('#panelDisplay').hide();
  $('.dList').hide();
});
function gotoAttributeDetails(a) {
  $('#attributeList').hide();
  $('#panelDisplay').show();
  $('#'+a).show();
}
function gotoAttribute(a) {
  $('#'+a).hide();
  $('#panelDisplay').hide();
  $('#attributeList').show();
}
