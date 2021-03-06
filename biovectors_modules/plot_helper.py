from pathlib import Path
from typing import Any, Mapping, Sequence, Tuple, Iterable

import imageio
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotnine as p9
from plydata import query, define, if_else, pull
from wordcloud import WordCloud


def plot_local_global_distances(
    timeline_df: pd.DataFrame, token: str
) -> Tuple[p9.ggplot, p9.ggplot, p9.ggplot, p9.ggplot]:
    """
    This function is designed to create a line plot of a token's global and local distance.
    The global distance represents how the token vector itself is changing across the years,
    while the local distance represents how a token's similarity towards its neighbors
    change across the years.

    Parameters
        timeline_df - a panda dataframe containing tokens with local_distance, global_distance and the corresponding z-scores
    """
    timeline_df = timeline_df >> query("token==@token")

    text_color = (
        timeline_df
        >> define(text_color=if_else("global_dist >= 0.7", "'black'", "'white'"))
        >> pull("text_color")
    )

    global_distance_plot = (
        p9.ggplot(
            timeline_df, p9.aes(x="year_origin", y="year_compared", fill="global_dist")
        )
        + p9.geom_tile(p9.aes(width=1, height=1))
        + p9.geom_text(
            p9.aes(label="global_dist"), format_string="{:.2f}", color=text_color
        )
        + p9.labs(
            x="Year Start",
            y="Year End",
            title=f"Global Distance for '{token}'",
            fill="Global Dist",
        )
        + p9.theme_seaborn(style="ticks", context="paper")
        + p9.scale_fill_cmap(limits=[0, 1])
        + p9.theme(figure_size=(10, 8), text=p9.element_text(size=11))
    )

    text_color = (
        timeline_df
        >> define(text_color=if_else("local_dist >= 0.7", "'black'", "'white'"))
        >> pull("text_color")
    )

    local_distance_plot = (
        p9.ggplot(
            timeline_df, p9.aes(x="year_origin", y="year_compared", fill="local_dist")
        )
        + p9.geom_tile(p9.aes(width=1, height=1))
        + p9.geom_text(
            p9.aes(label="local_dist"), format_string="{:.2f}", color=text_color
        )
        + p9.labs(
            x="Year Start",
            y="Year End",
            title=f"Local Distance for '{token}'",
            fill="Local Dist",
        )
        + p9.theme_seaborn(style="ticks", context="paper")
        + p9.scale_fill_cmap(limits=[0, 1])
        + p9.theme(figure_size=(10, 8), text=p9.element_text(size=11))
    )

    text_color = (
        timeline_df
        >> define(text_color=if_else("z_global_dist >= 2", "'black'", "'white'"))
        >> pull("text_color")
    )

    z_global_distance_plot = (
        p9.ggplot(
            timeline_df,
            p9.aes(x="year_origin", y="year_compared", fill="z_global_dist"),
        )
        + p9.geom_tile(p9.aes(width=1, height=1))
        + p9.geom_text(
            p9.aes(label="z_global_dist"), format_string="{:.2f}", color=text_color
        )
        + p9.labs(
            x="Year Start",
            y="Year End",
            title=f"Z-score Global Distance for '{token}'",
            fill="Z(Global Dist)",
        )
        + p9.theme_seaborn(style="ticks", context="paper")
        + p9.scale_fill_cmap(limits=[-3, 3])
        + p9.theme(figure_size=(10, 8), text=p9.element_text(size=11))
    )

    text_color = (
        timeline_df
        >> define(text_color=if_else("z_local_dist >= 2", "'black'", "'white'"))
        >> pull("text_color")
    )

    z_local_distance_plot = (
        p9.ggplot(
            timeline_df, p9.aes(x="year_origin", y="year_compared", fill="z_local_dist")
        )
        + p9.geom_tile(p9.aes(width=1, height=1))
        + p9.geom_text(
            p9.aes(label="z_local_dist"), format_string="{:.2f}", color=text_color
        )
        + p9.labs(
            x="Year Start",
            y="Year End",
            title=f"Z-score Local Distance for '{token}'",
            fill="Z(Local Dist)",
        )
        + p9.theme_seaborn(style="ticks", context="paper")
        + p9.scale_fill_cmap(limits=[-3, 3])
        + p9.theme(figure_size=(10, 8), text=p9.element_text(size=11))
    )

    return (
        global_distance_plot,
        local_distance_plot,
        z_global_distance_plot,
        z_local_distance_plot,
    )


def plot_token_timeline(timeline_df: pd.DataFrame) -> p9.ggplot:
    """
    This function is designed to plot a tsne projection of each word vector across the years.

    Parameters
        timeline_df - a panda dataframe containing the main token along with its neighbors
    """

    # Title of the plot
    token_title = timeline_df.query("label=='main'").iloc[0]["token"].upper()
    token_title = f"{token_title} Timeline"

    # Plotnine is awesome
    # Generate the plot
    g = (
        p9.ggplot(
            timeline_df.query("label=='main'"),
            p9.aes(x="umap_dim1", y="umap_dim2", label="year"),
        )
        + p9.geom_text(
            size=8,
            ha="left",
            va="baseline",
            position=p9.position_nudge(x=0.04, y=-0.01),
        )
        + p9.geom_point(size=1)
        + p9.theme(
            axis_line=p9.element_blank(),
            axis_line_x=p9.element_blank(),
            axis_line_y=p9.element_blank(),
            panel_grid=p9.element_blank(),
            panel_background=p9.element_rect(fill="white"),
        )
        + p9.labs(title=token_title)
        + p9.xlim(
            [
                np.floor(timeline_df.umap_dim1.min()),
                np.ceil(timeline_df.umap_dim1.max()),
            ]
        )
    )

    return g


def plot_wordcloud_neighbors(
    timeline_df: pd.DataFrame,
    num_plots_per_row: int = 3,
    plot_filename: str = "token_neighbors.png",
):
    """
    This function is designed to make a plot with each word cloud as a subplot.
    The issue here is the resolution can be wonky, but still important to have enabled.

    Parameters
        timeline_df - a panda dataframe containing the main token along with its neighbors
        num_plots_per_row - the number of subplots to have per row
        plot_filename - the name of the png file to be saved
    """

    # create the figures and sort the years
    plt.figure(figsize=(10, 10))
    years = timeline_df.sort_values("year").year.unique()
    token = timeline_df.iloc[0].token.upper()

    # Get the number of subplots per row
    num_plots = num_plots_per_row
    rows = int(np.ceil(len(years) / num_plots))

    # Plot the word clouds
    for idx, year in enumerate(years):
        neighbors = timeline_df.query(f"label=='neighbor'&year=='{year}'")
        token_text = dict(
            zip(
                neighbors.token.tolist(), [1 for idx in range(neighbors.token.shape[0])]
            )
        )

        i = idx + 1
        wc = WordCloud(
            background_color="white", color_func=lambda *args, **kwargs: (43, 140, 190)
        )
        wc.generate_from_frequencies(token_text)
        plt.plot()
        plt.subplot(rows, num_plots, i).set_title(year)
        plt.imshow(wc)
        plt.axis("off")
        plt.suptitle(f"{token} Neighbors", fontsize=20)

    plt.savefig(
        plot_filename, dpi=75, bbox_inches="tight", transparent="True", pad_inches=0
    )


def plot_wordcloud_neighbors_gif(
    timeline_df: pd.DataFrame,
    piece_folder: str = "output/gif_pieces",
    plot_filename: str = "token_neighbors.gif",
):
    """
    This function is designed to generate a gif of word clouds for each token analyzed in this project.
    Gif is desired as one doesnt have to worry about resolution issues compared to the
    making multiple subplots.

    Parameters
        timeline_df - a panda dataframe containing the main token along with its neighbors
        piece_folder - the folder to hold temporary files to make the gif
        plot_filename - the name of the gif file to be saved
    """
    # Create the folder
    Path(piece_folder).mkdir(parents=True, exist_ok=True)

    # Get the years to analyze
    years = timeline_df.sort_values("year").year.unique()

    # Plot the frames for the gif
    for idx, year in enumerate(years):
        neighbors = timeline_df.query(f"label=='neighbor'&year=='{year}'")
        token_text = dict(
            zip(
                neighbors.token.tolist(), [1 for idx in range(neighbors.token.shape[0])]
            )
        )

        wc = WordCloud(
            background_color="white", color_func=lambda *args, **kwargs: (43, 140, 190)
        )
        wc.generate_from_frequencies(token_text)
        plt.figure(figsize=(10, 10))
        plt.imshow(wc)
        plt.title(f"Year: {year}", fontsize=22)
        plt.axis("off")

        plt.savefig(
            f"{piece_folder}/{idx}.png",
            dpi=75,
            bbox_inches="tight",
            transparent="True",
            pad_inches=0,
        )
        plt.close()

    # Create the gif
    with imageio.get_writer(
        plot_filename, mode="I", format="GIF-FI", duration=3, quantizer="nq"
    ) as writer:
        gif_pieces = list(Path(piece_folder).rglob("*png"))
        for file in sorted(gif_pieces, key=lambda x: int(x.stem)):
            writer.append_data(imageio.imread(str(file)))
