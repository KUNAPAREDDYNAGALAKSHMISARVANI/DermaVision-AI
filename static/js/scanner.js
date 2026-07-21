/*
==========================================================
 DermaVision AI
 AI Scanning Animation
==========================================================
*/

document.addEventListener("DOMContentLoaded", function(){

    const forms = document.querySelectorAll(
        "form[action*='predict']"
    );

    if(!forms.length) return;


    forms.forEach(function(form){

        form.addEventListener("submit", function(){

            startScanner();

        });

    });


});


function startScanner(){

    const overlay = document.createElement("div");

    overlay.className="ai-scanner-overlay";


    overlay.innerHTML = `

        <div class="scanner-container">


            <div class="scanner-logo">

                <i class="fas fa-brain"></i>

            </div>


            <h2>

                AI Skin Analysis

            </h2>


            <p id="scanText">

                Preparing image...

            </p>


            <div class="scan-image">

                <div class="scan-line"></div>

                <i class="fas fa-user-doctor"></i>

            </div>


            <div class="scan-loader">

                <span></span>
                <span></span>
                <span></span>

            </div>


        </div>

    `;


    document.body.appendChild(overlay);



    const messages=[

        "Preparing image...",

        "Detecting skin patterns...",

        "Analyzing visual features...",

        "Comparing AI learned patterns...",

        "Generating dermatology report..."

    ];


    let index=0;


    const text=document.getElementById(
        "scanText"
    );


    setInterval(function(){

        if(index < messages.length){

            text.innerHTML=messages[index];

            index++;

        }

    },1200);


}
/* ==========================================================
   Scanner Status Animation
========================================================== */


function updateScannerProgress(){

    const progressMessages = [

        {
            icon:"fa-image",
            text:"Loading skin image..."
        },

        {
            icon:"fa-magnifying-glass",
            text:"Extracting skin features..."
        },

        {
            icon:"fa-dna",
            text:"Analyzing visual patterns..."
        },

        {
            icon:"fa-brain",
            text:"Running AI prediction model..."
        },

        {
            icon:"fa-file-medical",
            text:"Preparing medical report..."
        }

    ];


    let current = 0;


    const textElement =
    document.getElementById("scanText");


    const iconElement =
    document.querySelector(".scanner-logo i");


    const interval =
    setInterval(function(){


        if(!textElement || !iconElement){

            clearInterval(interval);

            return;

        }


        textElement.innerHTML =
        progressMessages[current].text;


        iconElement.className =
        "fas " +
        progressMessages[current].icon;



        current++;


        if(current >= progressMessages.length){

            clearInterval(interval);

        }


    },1200);


}



/* ==========================================================
   Start Animation
========================================================== */


function startScanner(){


    const overlay =
    document.createElement("div");


    overlay.className =
    "ai-scanner-overlay";


    overlay.innerHTML = `


    <div class="scanner-container">


        <div class="scanner-logo">

            <i class="fas fa-brain"></i>

        </div>


        <h2>

            AI Skin Analysis

        </h2>


        <p id="scanText">

            Initializing AI scanner...

        </p>
        <div class="scan-image">

    <img
        id="scannerPreviewImage"
        src=""
        alt="Scanning Image"
    >

    <div class="scan-line"></div>

</div>
        <div class="scan-loader">


            <span></span>

            <span></span>

            <span></span>


        </div>



    </div>


    `;

    document.body.appendChild(overlay);
    const preview = document.getElementById("previewImage");
    const scannerImage = document.getElementById("scannerPreviewImage");

if (preview && preview.src) {
    scannerImage.src = preview.src;
}

    updateScannerProgress();


}