import React from 'react';
import ReactDom from 'react-dom';

import DatabasesTable from './databases/table';
//import DomainAdd from  './domains/add';

var addDialog;
var databasesTable;

var el = document.getElementById('databases-table');
databasesTable = ReactDom.render(<DatabasesTable />, el);

function refreshDomainsTable() {
  databasesTable.fetch()
}

$('#domain-add-button').click( (e) =>{
  e.preventDefault();
  var el = document.getElementById('domains-add');
  if(!addDialog){
    addDialog = ReactDom.render(<DomainAdd onClose={refreshDomainsTable}/>, el);
  }
  addDialog.show();
});
