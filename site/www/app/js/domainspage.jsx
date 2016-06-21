/* global $ */
import React from 'react';
import ReactDom from 'react-dom';


import DomainsTable from './domains/table';
import ActionHeader from './common/actionheader';
import DomainAdd from './domains/add';

class DomainsPage extends React.Component {
  showError = (error) => {
    this.refs.actionHeaderRef.showError(error);
  }
  render() {
    return (<div>
      <ActionHeader
        ref="actionHeaderRef"
        buttons={[
          { name: 'Add', title: 'Add new domain', onClick: () => this.refs.addDialog.show() },
        ]}
      />
      <DomainsTable ref="domainsTable" showError={this.showError} />
      <DomainAdd ref="addDialog" title="Add new domain" onClose={() => this.refs.domainsTable.fetch()} />
    </div>);
  }
}


ReactDom.render(
  <DomainsPage />,
  document.getElementById('domains-table')
);
