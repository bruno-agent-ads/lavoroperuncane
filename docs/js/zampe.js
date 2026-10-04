/* La gara delle zampine: aggiornare "voti" a mano ogni sera, contando i client_reference_id dei pagamenti su Stripe.
   prov = sigla della provincia sulla mappa; lat/lon = dove sta il rifugio. */
window.ZAMPE=[
  {ref:'qua-la-zampa',  emo:'🐶', nome:'Qua la Zampa onlus', dove:"San Quirico d'Orcia (SI)", prov:'SI', lat:43.058, lon:11.605, voti:2},
  {ref:'occhi-di-gatto',emo:'🐱', nome:'Occhi di Gatto',     dove:'Grosseto',                 prov:'GR', lat:42.760, lon:11.113, voti:0},
  {ref:'enpa-valdarno', emo:'🐾', nome:'ENPA Valdarno',      dove:'Valdarno (AR)',            prov:'AR', lat:43.565, lon:11.530, voti:0}
];
/* Il giro di Toscana. Quando a fine mese un rifugio riceve il bonifico:
   1) aggiungilo qui sotto in "aiutate" con gli euro VERI del bonifico,
   2) toglilo da ZAMPE e metti al suo posto il rifugio della provincia nuova. */
window.GIRO={
  regione:'Toscana',
  aiutate:[
    /* esempio: {prov:'SI', nome:'Qua la Zampa onlus', euro:0, mese:'ottobre 2026'} */
  ],
  /* La tombola: i nomi più proposti nei commenti (massimo 6). Vuota = monete col punto di domanda. */
  candidati:[
    /* esempio: {nome:'Rifugio dei ciuchi', dove:'Pisa', emo:'🫏'} */
  ]
};
