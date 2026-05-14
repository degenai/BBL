$(document).ready(function() {
  //ページャー
  var pagerConfig = {
  multi : "card",
  mode : 1,
  pagerName : ".pager",
  targetCol : ".list-inner li",
  prevName : ".prevBtn",
  nextName : ".nextBtn",
  firstName : ".firstBtn",
  pcPageItems : 20,
  spPageItems : 20,
  pcViewNum : 10,
  spViewNum : 5,
  breakPoint : 1024,
  };
  pagerSet(pagerConfig);

	$('.pager:eq(1)').click(function() {
    var target = $("#listCol");
    if (target) {
        var targetOffset = target.offset().top;
        $('html,body').animate({scrollTop: targetOffset},400,"easeInOutQuart");
        return false;
        }
    });
  
  
  //表面 裏面の切り替え
  $('.btn_back').click(
    function(event){
      //消すもの
      $(this).parents('.list-inner li').find('.cardFront').hide();//表面
      //出すもの
      $(this).parents('li').find('.cardBack').fadeIn("fast");//裏面
    }
  );
  $('.btn_front').click(
    function(event){
      //消すもの
      $(this).parents('.list-inner li').find('.cardBack').hide();//裏面
      //出すもの
      $(this).parents('.list-inner li').find('.cardFront').fadeIn("fast");//表面
    }
  );
});

////カードリスト文字数制御
//--------------------------------------------------------------------
$( function() {
	$(".seriesCol dd").each(function(){
        //文字以上だったら
    if ($(this).text().length > 23) {
        //文字サイズを修正
        $(this).css('fontSize','88%');
        }
    });
    $(".specialTraitCol dd").each(function(){
        //文字以上だったら
    if ($(this).text().length > 23) {
        //文字サイズを修正
        $(this).css('fontSize','82%');
        }
    });
    $(".eraCol dd").each(function(){
        //文字以上だったら
    if ($(this).text().length > 23) {
        //文字サイズを修正
        $(this).css('fontSize','82%');
        }
    });
});

// フォーム入力内容クリア
function inputFromClear() {
// KeyWord Search
document.getElementById('free').value='';
// Card Name
document.getElementById('card').value='';
// Series
document.getElementsByName('category_exp')[0][0].selected = true;
// Card Type
document.getElementsByName('rank')[0][0].selected = true;
// Energy
document.getElementsByName('energy')[0][0].selected = true;
// Combo Energy
document.getElementsByName('comboEnergy')[0][0].selected = true;
// Combo Power
document.getElementsByName('comboPower')[0][0].selected = true;
// Power
document.getElementsByName('power')[0][0].selected = true;
// Rarity
document.getElementsByName('rarity')[0][0].selected = true;
// Color
document.getElementsByName('attribute')[0][0].selected = true;
// Character
document.getElementsByName('character')[0][0].selected = true;
// Character2
document.getElementsByName('character2')[0][0].selected = true;
document.getElementsByName('character2')[0].disabled = true;
// Special Trait
document.getElementsByName('specialTrait')[0][0].selected = true;
// Era
document.getElementsByName('era')[0][0].selected = true;
// Keyword skill
document.getElementsByName('keywordSkill')[0][0].selected = true;
}