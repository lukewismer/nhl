{data: 'info.shoots_catches', orderable: true},
          {data: function(data, type, row){
              return data['nhl_stats'][-1]['team_name'];
          }, orderable: true},
          {data: 'info.number', orderable: true},
          {data: 'nhl_stats[-1].year', orderable: true},
          {data: 'nhl_stats[-1].stats.games_played', orderable: true},
          {data: 'nhl_stats[-1].stats.goals', orderable: true},
          {data: 'nhl_stats[-1].stats.assists', orderable: true},
          {data: 'nhl_stats[-1].stats.points', orderable: true},
          {data: 'nhl_stats[-1].stats.shots', orderable: true},
          {data: 'nhl_stats[-1].stats.hits', orderable: true},
          {data: 'nhl_stats[-1].stats.pims', orderable: true},
          {data: 'nhl_stats[-1].stats.plus_minus', orderable: true},
          {data: 'nhl_stats[-1].stats.blocks', orderable: true},


          <th>Hand</th>
        <th>Team</th>
        <th>#</th>
        <th>Season</th>
        <th>GP</th>
        <th>G</th>
        <th>A</th>
        <th>P</th>
        <th>S</th>
        <th>H</th>
        <th>PIM</th>
        <th>+/-</th>
        <th>Blocks</th>