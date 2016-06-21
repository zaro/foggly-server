import React from 'react';
import ReactDom from 'react-dom';

import DatabasesTable from './databases/table';
import ActionHeader from './common/actionheader';
import DatabaseAdd from './databases/add';

class DatabasesPage extends React.Component {
  showError = (error) => {
    this.refs.actionHeaderRef.showError(error);
  }
  render() {
    return (<div>
      <ActionHeader
        ref="actionHeaderRef"
        buttons={[
          { name: 'Add', title: 'Add new database', onClick: () => this.refs.addDialog.show() },
        ]}
      />
      <DatabasesTable ref="dbTable" showError={this.showError} />
      <DatabaseAdd ref="addDialog" title="Add Mysql Database" onClose={() => this.refs.dbTable.fetch()} />
    </div>);
  }
}


ReactDom.render(
  <DatabasesPage />,
  document.getElementById('databases-table')
);
