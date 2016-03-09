import React from 'react';
import ReactDom from 'react-dom';

import DomainsTable from './domains/table';
import DomainAdd from  './domains/add';

var addDialog;
var domainsTable;

var el = document.getElementById('domains-table');
domainsTable = ReactDom.render(<DomainsTable />, el);

function refreshDomainsTable() {
  domainsTable.fetch()
}

$('#domain-add-button').click( (e) =>{
  e.preventDefault();
  var el = document.getElementById('domains-add');
  if(!addDialog){
    addDialog = ReactDom.render(<DomainAdd onClose={refreshDomainsTable}/>, el);
  }
  addDialog.show();
});
