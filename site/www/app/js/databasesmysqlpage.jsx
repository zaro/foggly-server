/* global $,_ */
import React from 'react';
import ReactDom from 'react-dom';

import DatabasesTable from './databases/table';
import DomainAdd from './domains/add';

let addDialog;

const databasesTable = ReactDom.render(<DatabasesTable />, document.getElementById('databases-table'));

function refreshDomainsTable() {
  databasesTable.fetch();
}

$('#domain-add-button').click( (e) => {
  const el = document.getElementById('domains-add');
  if (!addDialog) {
    addDialog = ReactDom.render(<DomainAdd onClose={refreshDomainsTable} />, el);
  }
  addDialog.show();
  e.preventDefault();
});
