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
 var quickFormLink=document.querySelector(".actionbar a[href^=\"#\"]");
 if(quickFormLink) quickFormLink.setAttribute("href","#"+lang+"-form");
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
 var fallback=form.querySelector(".std-fallback");
 var emailLink=fallback&&fallback.querySelector("[data-email-fallback]");
 var copyButton=fallback&&fallback.querySelector("[data-copy-fallback]");
 var copyFeedback=fallback&&fallback.querySelector("[data-copy-feedback]");
 var copyLabel=fallback&&fallback.querySelector(".std-copy-label");
 var copyText=fallback&&fallback.querySelector("[data-copy-text]");
 var isArabic=form.getAttribute("data-form-lang")==="ar";
 var fallbackBody="";
 var fallbackEmail="alaa.qadir@crownsmere.com";
 var archiveEmail="hello@crownsmere.com";
 function enquirySummary(data){
  var choices={
   service:{
    "Apartment and guarantor help":["Apartment search and guarantor guidance","البحث عن شقة والمساعدة في خيارات الضمان"],
    "Guarantor guidance for found property":["Guarantor guidance for a property already found","المساعدة في خيارات الضمان لعقار وجدته"],
    "Apartment search only":["Apartment search only","البحث عن شقة للإيجار فقط"]
   },
   monthly_budget:{
    "Not decided":["Not decided yet","لم أحدد الميزانية بعد"],
    "Under GBP 1500":["Under £1,500 per month","أقل من £1,500 شهرياً"],
    "GBP 1500-2500":["£1,500–£2,500 per month","من £1,500 إلى £2,500 شهرياً"],
    "GBP 2500-4000":["£2,500–£4,000 per month","من £2,500 إلى £4,000 شهرياً"],
    "Over GBP 4000":["Over £4,000 per month","أكثر من £4,000 شهرياً"]
   },
   move_timeframe:{
    "As soon as possible":["As soon as possible","في أقرب وقت ممكن"],
    "Within 1 month":["Within one month","خلال شهر واحد"],
    "Within 1-3 months":["Within 1–3 months","خلال شهر إلى ثلاثة أشهر"],
    "Later/unsure":["Later / not sure yet","لاحقاً / لم أحدد بعد"]
   },
   guarantor_status:{
    "No UK guarantor":["I do not have a UK guarantor","ليس لدي ضامن في المملكة المتحدة"],
    "Potential overseas family guarantor":["I may have a family guarantor overseas","قد يستطيع أحد أفراد عائلتي خارج المملكة المتحدة أن يكون ضامناً"],
    "Exploring professional guarantor":["I want advice about professional guarantor services","أرغب في معرفة خدمات الضامن المهني"],
    "Unsure":["I am not sure yet","لست متأكداً بعد"]
   },
   property_found:{
    "Need to find a property":["Not yet — please help me search","لم أجد عقاراً بعد وأحتاج للمساعدة في البحث"],
    "Already found a property":["Yes — I have a particular property in mind","نعم، وجدت عقاراً محدداً"],
    "Comparing options":["Still comparing properties","ما زلت أقارن بين العقارات"]
   },
   preferred_contact:{
    "Email":["Email","البريد الإلكتروني"],
    "Phone":["Telephone call","مكالمة هاتفية"],
    "WhatsApp":["WhatsApp","واتساب"]
   }
  };
  function value(name){
   var raw=String(data[name]||"").trim();
   var mapped=choices[name]&&choices[name][raw];
   return mapped?mapped[isArabic?1:0]:raw;
  }
  function line(label,name,optional){
   var result=value(name);
   return result||!optional?label+": "+(result||(isArabic?"غير محدد":"Not provided")):"";
  }
  function section(title,lines){
   var present=lines.filter(Boolean);
   return present.length?title+"\n"+present.join("\n"):"";
  }
  var name=String(data.name||"").trim();
  var sections=isArabic?[
   section("بيانات الطالب",[line("الاسم الكامل","name"),line("الجامعة أو الكلية","university",true)]),
   section("متطلبات السكن",[
    line("نوع المساعدة المطلوبة","service"),
    line("ميزانية الإيجار الشهرية","monthly_budget"),
    line("موعد الانتقال","move_timeframe"),
    line("المناطق المفضلة في لندن","preferred_areas",true),
    line("حالة البحث عن العقار","property_found")
   ]),
   section("وضع الضامن",[line("الضامن المتاح","guarantor_status")]),
   section("معلومات التواصل",[
    line("البريد الإلكتروني","email"),line("رقم الهاتف أو واتساب","phone",true),
    line("طريقة التواصل المفضلة","preferred_contact")
   ]),
   value("additional_notes")?section("تفاصيل إضافية",[value("additional_notes")]):""
  ]:[
   section("STUDENT DETAILS",[line("Full name","name"),line("University / college","university",true)]),
   section("RENTAL REQUIREMENTS",[
    line("Assistance required","service"),
    line("Monthly rental budget","monthly_budget"),
    line("Preferred move-in time","move_timeframe"),
    line("Preferred London areas","preferred_areas",true),
    line("Property search status","property_found")
   ]),
   section("GUARANTOR SITUATION",[line("Current situation","guarantor_status")]),
   section("CONTACT DETAILS",[
    line("Email address","email"),line("Phone / WhatsApp","phone",true),
    line("Preferred contact method","preferred_contact")
   ]),
   value("additional_notes")?section("ADDITIONAL NOTES",[value("additional_notes")]):""
  ];
  var introduction=isArabic
   ?"مرحباً أستاذة علا،\n\nأنا طالب دولي وأرغب في مساعدتكم في إيجار عقار في لندن أو معرفة خيارات الضامن المناسبة. فيما يلي تفاصيل طلبي:"
   :"Dear Alaa,\n\nI am an international student seeking assistance with renting a home in London and/or understanding UK guarantor options. Please find my requirements below.";
  var end=isArabic
   ?"أرجو التواصل معي لمناقشة الخيارات المتاحة.\n\nمع خالص التحية،\n"+name
   :"I would appreciate your guidance and look forward to hearing from you.\n\nKind regards,\n"+name;
  var origin=isArabic
   ?"أُعدّت هذه الرسالة عبر نموذج الطلاب في crownsmere.com/students.html"
   :"Prepared using the student enquiry form at crownsmere.com/students.html";
  return introduction+"\n\n"+sections.filter(Boolean).join("\n\n")+"\n\n"+end+"\n\n"+origin;
 }
 function showFallback(data){
  if(!fallback)return "";
  fallbackBody=enquirySummary(data);
  var who=String(data.name||"").replace(/[\r\n<>]/g," ").trim().slice(0,75);
  var subject=isArabic
   ?"Crownsmere Estate | طلب سكن للطلاب الدوليين | "+who
   :"Crownsmere Estate | International Student Rental Enquiry | "+who;
  var mailto="mailto:"+fallbackEmail
   +"?cc="+encodeURIComponent(archiveEmail)
   +"&subject="+encodeURIComponent(subject)
   +"&body="+encodeURIComponent(fallbackBody);
  if(emailLink)emailLink.setAttribute("href",mailto);
  if(copyText)copyText.value="To: "+fallbackEmail+"\nCc: "+archiveEmail+"\nSubject: "+subject+"\n\n"+fallbackBody;
  if(copyFeedback)copyFeedback.textContent="";
  if(copyLabel)copyLabel.hidden=true;
  fallback.hidden=false;
  return mailto;
 }
 if(copyButton){
  copyButton.addEventListener("click",function(){
   var text=copyText?copyText.value:fallbackBody;
   if(!text)return;
   function copied(){if(copyFeedback)copyFeedback.textContent=isArabic
    ?"تم نسخ الطلب. الصقه في رسالة بريد إلى علا واضغط إرسال."
    :"Enquiry copied. Paste it into an email to Alaa and press Send.";}
   function manual(){
    if(copyLabel)copyLabel.hidden=false;
    if(copyText){copyText.focus();copyText.select();}
    if(copyFeedback)copyFeedback.textContent=isArabic
     ?"إذا تعذر النسخ تلقائياً، حدد النص أدناه وانسخه إلى رسالة بريد إلكتروني."
     :"If copying was blocked, select the text below and copy it into an email.";
   }
   if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).then(copied,manual);
   }else{
    manual();
   }
  });
 }
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
  if(fallback)fallback.hidden=true;
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
   return response.json().then(function(body){return {ok:response.ok,body:body};});
  }).then(function(response){
   // A 200 HTML anti-bot challenge, JSON without success, or an API error is NOT delivery.
   var confirmation=response.body && response.body.success;
   if(!response.ok || (confirmation!==true && confirmation!=="true"))throw new Error("Delivery not confirmed");
   form.querySelector(".student-progress").hidden=true;
   stages.forEach(function(stage){stage.hidden=true;stage.classList.remove("is-active");});
   complete.hidden=false;
   if(fallback)fallback.hidden=true;
   say("");
   form.reset();
   complete.focus({preventScroll:true});
   complete.scrollIntoView({block:"center",behavior:"smooth"});
  }).catch(function(){
   say(status.getAttribute("data-error"),true);
   showFallback(data);
  }).then(function(){sending=false;submit.disabled=false;});
 });
 show(0,false);
});
})();