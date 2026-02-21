export const puckConfig = {
  components: {
    Text: {
      fields: {
        text: { type: "text" }
      },
      render: ({ text }) => <p>{text}</p>
    },
    Section: {
      fields: {
        title: { type: "text" },
        content: { type: "text" }
      },
      render: ({ title, content }) => (
        <section>
          <h2>{title}</h2>
          <div>{content}</div>
        </section>
      )
    }
  }
};
