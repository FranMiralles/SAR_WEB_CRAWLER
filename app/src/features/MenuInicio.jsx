import "./MenuInicio.css"

export function MenuInicio() {
  return (
    <div className="divCentralMenuInicio">
      <div className="divMenuInicio">
        <ItemMenu name={"CRAWLER"} />
        <ItemMenu name={"INDEXER"} />
        <ItemMenu name={"SEARCHER"} />
      </div>
    </div>
  );
}

function ItemMenu(props) {
  return (
    <div className="divItemMenu">
      <button className="buttonItemMenu">{props.name}</button>
    </div>
  );
}

