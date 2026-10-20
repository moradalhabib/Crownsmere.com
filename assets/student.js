/* Crownsmere student enquiry: progressive enhancement, bilingual form, no third-party tracking. */
(function(){
"use strict";
var bar=document.querySelector(".student-language-bar");
if(!bar) return;
var panels=Array.prototype.slice.call(document.querySelectorAll("[data-language-panel]"));
var switches=Array.prototype.slice.call(document.querySelectorAll("[data-lang-switch]"));
var qs=new URLSearchParams(window.location.search);
var lang=qs.get("lang")==="ar"?"ar":"en";
function setLanguage(value){
 lang=value==="ar"?"ar":"en";
 panels.forEach(function(panel){panel.hidden=panel.getAttribute("data-language-panel")!==lang;});
 switches.forEach(function(button){
  var active=button.getAttribute("data-lang-switch")===lang;
  button.classList.toggle("is-active",active);
  button.setAttribute("aria-pressed",String(active));
 });
 // Keep navigation and the centred Crownsmere logo in their original LTR layout.
 // Each language panel already has its own lang and dir attributes.
 document.documentElement.lang="en-GB";
 document.documentElement.dir="ltr";
}
switches.forEach(function(button){
 button.addEventListener("click",function(){setLanguage(button.getAttribute("data-lang-switch"));});
});
setLanguage(lang);
document.querySelectorAll(".student-form").forEach(function(form){
 var stages=Array.prototype.slice.call(form.querySelectorAll("[data-student-step]"));
 var indicators=Array.prototype.slice.call(form.querySelectorAll("[data-step-indicator]"));
 var status=form.querySelector(".std-status");
 var complete=form.querySelector(".std-sent");
 var submit=form.querySelector('[type="submit"]');
 var current=0,sending=false;
 form.noValidate=true; // Custom validation accounts for hidden wizard steps.
 form.classList.add("enhanced");
 function say(message,error){
  status.textContent=message||"";
  status.classList.toggle("is-error",!!error);
 }
 function phoneValid(){
  var phone=form.querySelector('input[name="phone"]'),pref=form.querySelector('input[name="preferred_contact"]:checked');
  var needsNumber=pref && pref.value!=="Email";
  var digits=(phone.value||"").replace(/\D/g,"");
  var valid=(!needsNumber&&!phone.value)||(/^[0-9+() .-]+$/.test(phone.value)&&digits.length>=7&&digits.length<=15);
  phone.setCustomValidity(valid?"":status.getAttribute("data-phone"));
  return valid;
 }
 function fieldsValid(scope,showErrors){
  phoneValid();
  var bad=Array.prototype.slice.call(scope.querySelectorAll("input,select,textarea")).find(function(el){
   return el.type!=="hidden" && el.type!=="button" && !el.checkValidity();
  });
  if(bad && showErrors){
   say(bad.validationMessage||status.getAttribute("data-invalid"),true);
   bad.focus();
  }
  return !bad;
 }
 function show(index,focus){
  current=Math.max(0,Math.min(stages.length-1,index));
  stages.forEach(function(stage,i){
   stage.classList.toggle("is-active",i===current);
   stage.hidden=i!==current;
  });
  indicators.forEach(function(li,i){
   li.classList.toggle("is-complete",i<current);
   if(i===current)li.setAttribute("aria-current","step");
   else li.removeAttribute("aria-current");
  });
  say("");
  if(focus){
   var heading=stages[current].querySelector("h3");
   if(heading)heading.focus({preventScroll:true});
   form.scrollIntoView({behavior:window.matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth",block:"start"});
  }
 }
 function firstInvalidStep(){
  for(var i=0;i<stages.length;i++)if(!fieldsValid(stages[i],false))return i;
  return -1;
 }
 form.addEventListener("click",function(e){
  var next=e.target.closest("[data-next]"),back=e.target.closest("[data-back]");
  if(next){if(fieldsValid(stages[current],true))show(current+1,true);}
  if(back)show(current-1,true);
 });
 form.addEventListener("keydown",function(e){
  if(e.key==="Enter"&&e.target.tagName==="INPUT"&&e.target.type!=="radio"&&e.target.type!=="checkbox"&&current<stages.length-1){
   e.preventDefault();if(fieldsValid(stages[current],true))show(current+1,true);
  }
 });
 form.addEventListener("submit",function(e){
  e.preventDefault();
  if(sending)return;
  var bad=firstInvalidStep();
  if(bad!==-1){
   if(bad!==current)show(bad,true);
   fieldsValid(stages[bad],true);
   return;
  }
  var data={};
  new FormData(form).forEach(function(value,key){data[key]=typeof value==="string"?value.trim():value;});
  if(data._honey){ // Avoid sending bot-filled forms to the inbox.
   say(status.getAttribute("data-invalid"),true);return;
  }
  delete data._honey;
  var endpoint=form.getAttribute("data-endpoint");
  if(!endpoint){say(status.getAttribute("data-error"),true);return;}
  sending=true;submit.disabled=true;
  say(status.getAttribute("data-sending"));
  fetch(endpoint,{method:"POST",headers:{"Content-Type":"application/json","Accept":"application/json"},body:JSON.stringify(data)})
  .then(function(response){
   return response.json().catch(function(){return {};}).then(function(body){return {ok:response.ok,body:body};});
  }).then(function(response){
   if(!response.ok||String(response.body.success)==="false")throw new Error("Delivery failed");
   form.querySelector(".student-progress").hidden=true;
   stages.forEach(function(stage){stage.hidden=true;stage.classList.remove("is-active");});
   complete.hidden=false;
   say("");
   form.reset();
   complete.focus({preventScroll:true});
   complete.scrollIntoView({block:"center",behavior:"smooth"});
  }).catch(function(){
   say(status.getAttribute("data-error"),true);
  }).then(function(){sending=false;submit.disabled=false;});
 });
 show(0,false);
});
})();