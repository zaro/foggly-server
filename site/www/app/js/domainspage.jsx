/* global $ */
import React from 'react';
import ReactDom from 'react-dom';

import DomainsTable from './domains/table';
import DomainAdd from './domains/add';

let addDialog;

const domainsTable = ReactDom.render(<DomainsTable />, document.getElementById('domains-table'));

function refreshDomainsTable() {
  domainsTable.fetch();
}

$('#domain-add-button').click((e) => {
  const el = document.getElementById('domains-add');
  if (!addDialog) {
    addDialog = ReactDom.render(<DomainAdd onClose={refreshDomainsTable} />, el);
  }
  addDialog.show();
  e.preventDefault();
});
