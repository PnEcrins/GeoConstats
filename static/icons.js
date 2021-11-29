// var constatIcon = L.divIcon({
//     html: `
//     <svg  
//         xmlns="http://www.w3.org/2000/svg"
//         preserveAspectRatio="none"
//         width="24"
//         height="40"
//         viewBox="0 0 100 100"
//     >
//     <rect x="0" y="0" width="20" height="20" />    `,
//     className: "",
//     iconSize: [24, 40],
//     iconAnchor: [12, 40],
//   });


// var declaratifIcon = L.divIcon({
//     html: `
//     <svg
//         xmlns="http://www.w3.org/2000/svg" 
//         width="100"
//         height="100"
//         version="1.1">
//     <circle cx="50" cy="50" r="10"/>
//     </svg>`,
//     className: "",
//     iconSize: [24, 40],
//     iconAnchor: [12, 40],
//   });

{/* <path d="M0 0 L50 100 L100 0 Z" fill="#7A8BE7"></path> */}

const declaratifIcon = L.divIcon({
    html: `
  <svg
    width="20"
    height="20"
    viewBox="0 0 20 20"
    version="1.1"
    preserveAspectRatio="none"
    xmlns="http://www.w3.org/2000/svg"
  >
  <path d="M10 10 H 90 V 90 H 10 L 10 10" fill="#7A8BE7"></path>
  </svg>`,
    className: "svg-icon",
    iconSize: [24, 40],
    iconAnchor: [12, 40],
  });

  const constatIcon = L.divIcon({
    html: `
  <svg
    width="24"
    height="40"
    viewBox="0 0 100 100"
    version="1.1"
    preserveAspectRatio="none"
    xmlns="http://www.w3.org/2000/svg"
  >
  <path d="M0 0 L50 100 L100 0 Z" fill="#7A8BE7"></path>
  </svg>`,
    className: "svg-icon",
    iconSize: [24, 40],
    iconAnchor: [12, 40],
  });


