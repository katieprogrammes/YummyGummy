document.addEventListener("DOMContentLoaded", function () {
    const menuIcon = document.getElementById("menu-icon");
    const midmenuIcon = document.getElementById("midmenu-icon");
    const mobileNav = document.getElementById("mobile-nav");
    

    menuIcon.addEventListener("click", function () {
        mobileNav.classList.toggle("active");
    });
    midmenuIcon.addEventListener("click", function () {
        mobileNav.classList.toggle("active");
    });


    
    document.getElementById('filterButton').addEventListener('click', function() {
        var filterSection = document.getElementById('filterSection');
        
        // Toggle between showing and hiding the filter section
        if (filterSection.classList.contains('show')) {
            filterSection.classList.remove('show');
        } else {
            filterSection.classList.add('show');
        }
    });
    
    
    
});