import React from 'react';
import ReactDom from 'react-dom';

import DomainsTable from './domains/table';
import DomainAdd from  './domains/add';

var el = document.getElementById('domains-table');
ReactDom.render(<DomainsTable />, el);

$('#domain-add-button').click( (e) =>{
  e.preventDefault();
  var el = document.getElementById('domains-add');
  var addDialog = ReactDom.render(<DomainAdd />, el);
  addDialog.show();
});
